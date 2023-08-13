import ast
import builtins
import contextlib
import dataclasses
import enum
import typing

from typing import Any

from p2g import err
from p2g import gbl
from p2g import nd
from p2g import stat
from p2g import symbol


UNDEF = gbl.sentinel()
GLOBAL = gbl.sentinel()
NONLOCAL = gbl.sentinel()


class NS(enum.IntEnum):
    MODULE = enum.auto()
    FUNCTION = enum.auto()
    CLASS = enum.auto()


@dataclasses.dataclass
class Namespace:
    parent: "Namespace"
    guts: typing.Dict
    nstype: NS

    def __init__(self, nstype=NS.MODULE):
        self.nstype = nstype
        self.guts = {}
        self.parent = typing.cast(Namespace, None)

    @property
    def is_function(self):
        return self.nstype == NS.FUNCTION

    @property
    def is_class(self):
        return self.nstype == NS.CLASS

    @property
    def is_module(self):
        return self.nstype == NS.MODULE

    def get(self, key):
        return self.guts.get(key, UNDEF)

    def __getitem__(self, key):
        return self.guts[key]

    def __setitem__(self, key, value):
        self.guts[key] = value

    def __delitem__(self, key):
        del self.guts[key]

    def __contains__(self, key):
        return key in self.guts


def scan_namespaces(ns):
    yield ns
    ns = ns.parent
    while ns:
        if not ns.is_class:
            yield ns
        ns = ns.parent


def resolve_nonlocal(name, ns):
    while ns:
        res = ns.get(name)
        if res is not UNDEF and res is not NONLOCAL:
            if ns.is_module:
                break
            return ns
        ns = ns.parent
    raise err.CompilerError(f"No binding for nonlocal '{name}'.")


def lookup_to_ns(res, self, nid):
    if res is GLOBAL:
        dstns = self.module_ns
    elif res is NONLOCAL:
        dstns = resolve_nonlocal(nid, self.ns.parent)
    else:
        dstns = self.ns
    return dstns


def find_ns(first_ns, nid):
    for ns in scan_namespaces(first_ns):
        res = ns.get(nid)
        if res is UNDEF:
            continue
        return res, ns
    return UNDEF, None


def _handle_visit_name_load(self, node):
    res, ns = find_ns(self.ns, node.id)
    if ns is None:
        try:
            return getattr(builtins, node.id)
        except AttributeError as exn:
            raise err.CompilerError(f"Name '{node.id}' is not defined.") from exn
    if res is GLOBAL:
        res = self.module_ns.get(node.id)
    elif res is NONLOCAL:
        ns = resolve_nonlocal(node.id, ns.parent)
        res = ns[node.id]
    assert res is not UNDEF
    symbol.Table.remember_load(node.id, res)
    return res


def handle_visit_name_del(self, node):
    res = self.ns.get(node.id)
    if res is UNDEF:
        err.compiler(f"Name '{node.id}' is not defined.")
    dstns = lookup_to_ns(res, self, node.id)
    del dstns[node.id]


def handle_visit_name_store(self, node, store_val):
    res = self.ns.get(node.id)
    if isinstance(res, nd.EBase):
        # variable is already in use, instead of
        # overwriting it,  treat as if writing to
        # <foo>.var
        #        breakpoint()
        setattr(res, "var", store_val)
        return
    dstns = lookup_to_ns(res, self, node.id)
    symbol.Table.remember_store(node.id, store_val)
    dstns[node.id] = store_val


def handle_visit_name(self, node):
    match node.ctx:
        case ast.Del():
            handle_visit_name_del(self, node)
        # in augmented assign, name arrives as with load ctx, but
        # must also be stored there, so catch both.
        case _:
            return _handle_visit_name_load(self, node)
    return None


@dataclasses.dataclass
class LoopContext:
    lcontinue: stat.Label
    lbreak: stat.Label
    lorelse: stat.Label
    prev: "LoopContext"

    def __init__(self, prev):
        self.prev = prev
        self.lcontinue = stat.next_label()
        self.lbreak = stat.next_label()
        self.lorelse = stat.next_label()


class WalkBase:
    ns: Namespace
    module_ns: Namespace
    file_name: str
    func_name: str

    def __init__(self):
        self.file_name = ""
        self.func_name = ""
        self.module_ns = Namespace()
        self.ns = self.module_ns
        self.loop = typing.cast(LoopContext, None)
        self.module_ns = typing.cast(Namespace, None)

    # def call(self, *_args, **_kwargs):
    #     raise NotImplementedError
    def visit_slist(self, lst):
        res = None
        for el in lst:
            res = self.visit(el)
        return res

    def update_lastplace(self, node):
        gbl.iface.last_node = node
        node.file_name = self.file_name

    def visit_fail(self, node, *_):
        name = node.__class__.__name__
        err.compiler(f"Feature '{name.lower()}' not implemented.")

    def _visit_return(self, node):
        if not self.ns.is_function:
            err.compiler("'return' outside function.")
        return self.visit(node.value)

    def visit(self, node) -> Any:
        if node is None:
            return None
        self.update_lastplace(node)
        method = "_visit_" + node.__class__.__name__.lower()
        visitor: typing.Callable[[ast.AST], Any] = getattr(self, method, self.visit_fail)

        return visitor(node)

    def visit_store(self, node, store_val) -> None:
        self.update_lastplace(node)
        method = "_visit_store_" + node.__class__.__name__.lower()
        visitor: typing.Callable[[ast.AST, ast.AST], None] = getattr(
            self, method, self.visit_fail
        )
        visitor(node, store_val)

    def _visit_expr(self, node):
        self.visit(node.value)

    @contextlib.contextmanager
    def pushpopns(self, ns):
        prev = self.ns
        self.ns = ns
        yield ns
        self.ns = prev

    def pushpop_with_parent(self, ns):
        ns.parent = self.ns
        return self.pushpopns(ns)

    def pushpop_funcns(self):
        return self.pushpop_with_parent(Namespace(NS.FUNCTION))

    def pushpop_classns(self):
        return self.pushpop_with_parent(Namespace(NS.CLASS))


class WalkNS(WalkBase):
    def _visit_global(self, node):
        for name in node.names:
            if name in self.ns and self.ns[name] is not GLOBAL:  # hard to test right
                err.compiler(f"Name '{name}' before global.")
            # Don't store GLOBAL in the top-level namespace
            if self.ns.parent:
                self.ns[name] = GLOBAL

    def _visit_nonlocal(self, node):
        if self.ns.is_module:  # hard to test right
            err.compiler("'nonlocal' declaration not allowed at module level.")
        for name in node.names:
            self.ns[name] = NONLOCAL
