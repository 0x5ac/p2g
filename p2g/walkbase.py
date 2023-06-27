import ast
import builtins
import contextlib
import dataclasses
import typing

from typing import Any

from p2g import err
from p2g import nd
from p2g import stat
from p2g import symbol


@dataclasses.dataclass
class VarScopeSentinel:
    name: str


UNDEF = VarScopeSentinel("nv")
GLOBAL = VarScopeSentinel("gbl")
NONLOCAL = VarScopeSentinel("nonlocal")


@dataclasses.dataclass
class ANamespace:
    parent: "ANamespace"
    guts: typing.Dict

    def __init__(self):
        self.guts = {}
        self.parent = typing.cast(ANamespace, None)

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


class ModuleNS(ANamespace):
    def __repr__(self):
        return "MODULE"  # for debug


class FunctionNS(ANamespace):
    pass


class ClassNS(ANamespace):
    pass


# return namespace and all the parents, filterint out
# parents which are classes.


def scan_namespaces(ns):
    yield ns
    ns = ns.parent
    while ns:
        if not isinstance(ns, ClassNS):
            yield ns

        ns = ns.parent


def resolve_nonlocal(name, ns):
    while ns:
        res = ns.get(name)
        if res is not UNDEF and res is not NONLOCAL:
            if isinstance(ns, ModuleNS):
                break
            return ns
        ns = ns.parent

    err.compiler(f"No binding for nonlocal '{name}'.")


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
        except AttributeError:
            err.compiler(f"Name '{node.id}' is not defined.")

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
    ns: "ANamespace"
    module_ns: "ModuleNS"
    file_name: str
    func_name: str

    def __init__(self):
        self.file_name = ""
        self.func_name = ""

        self.module_ns = ModuleNS()
        self.ns = self.module_ns
        self.loop = typing.cast(LoopContext, None)
        self.module_ns = typing.cast(ModuleNS, None)

    # def call(self, *_args, **_kwargs):
    #     raise NotImplementedError

    def visit_slist(self, lst):
        res = None
        for el in lst:
            res = self.visit(el)
        return res

    def update_lastplace(self, node):
        pos = err.NodePlace(
            node.col_offset,
            node.end_col_offset,
            node.lineno,
            self.func_name,
            self.file_name,
        )
        err.mark_pos(pos)

    def visit_fail(self, node, *_):
        name = node.__class__.__name__
        err.compiler(f"Feature '{name.lower()}' not implemented.")

    def _visit_return(self, node):
        if not isinstance(self.ns, FunctionNS):
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
        ns.parent = self.ns
        self.ns = ns
        yield
        self.ns = self.ns.parent


class WalkNS(WalkBase):
    def _visit_global(self, node):
        for n in node.names:
            if n in self.ns and self.ns[n] is not GLOBAL:  # hard to test right
                err.compiler(f"Name '{n}' before global.")
            # Don't store GLOBAL in the top-level namespace
            if self.ns.parent:
                self.ns[n] = GLOBAL

    def _visit_nonlocal(self, node):
        if isinstance(self.ns, ModuleNS):  # hard to test right
            err.compiler("'nonlocal' declaration not allowed at module level.")
        for n in node.names:
            self.ns[n] = NONLOCAL
