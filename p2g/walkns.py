import ast
import builtins
import dataclasses
import typing

from p2g import err
from p2g import nd
from p2g import vector


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


def resolve_nonlocal(self, name, ns):
    while ns:
        res = ns.get(name)
        if res is GLOBAL:
            return self.module_ns
        if res is not UNDEF and res is not NONLOCAL:
            if isinstance(ns, ModuleNS):
                break
            return ns
        ns = ns.parent
    err.compiler(f"no binding for nonlocal '{name}'")  # hard to test right
    return None


# return namespace and all the parents, filterint out
# parents which are classes.


def scan_namespaces(ns):
    yield ns
    ns = ns.parent
    while ns:
        if not isinstance(ns, ClassNS):
            yield ns

        ns = ns.parent


def find_ns(first_ns, nid):
    for ns in scan_namespaces(first_ns):
        res = ns.get(nid)
        if res is UNDEF:
            continue
        return res, ns
    return UNDEF, None


def lookup_to_ns(res, self, nid):
    if res is GLOBAL:
        dstns = self.module_ns
    elif res is NONLOCAL:
        dstns = resolve_nonlocal(self, nid, self.ns.parent)
    else:
        dstns = self.ns
    return dstns


def handle_visit_name_load(self, node):
    res, ns = find_ns(self.ns, node.id)
    if res is GLOBAL:
        res = self.module_ns.get(node.id)
    elif res is NONLOCAL:
        ns = resolve_nonlocal(self, node.id, ns.parent)
        return ns[node.id]
    if res is not UNDEF:
        return res

    try:
        return getattr(builtins, node.id)
    except AttributeError:
        err.compiler(f"{node.id} is not defined.")


def handle_visit_name_del(self, node):
    res = self.ns.get(node.id)
    if res is UNDEF:
        err.compiler(f"name '{node.id}' is not defined")

    dstns = lookup_to_ns(res, self, node.id)
    del dstns[node.id]


def handle_visit_name_store(self, node, store_val):
    res = self.ns.get(node.id)
    if isinstance(res, vector.ConstVec):
        err.compiler("Can't set a constant.")
    if isinstance(res, nd.EBase):
        # variable is already in use, instead of
        # overwriting it,  treat as if writing to
        # <foo>.var
        #        breakpoint()
        setattr(res, "var", store_val)
        return

    dstns = lookup_to_ns(res, self, node.id)
    dstns[node.id] = store_val


def handle_visit_name(self, node):
    match node.ctx:
        case ast.Del():
            handle_visit_name_del(self, node)
        # for both load and store when augmented
        case _:
            return handle_visit_name_load(self, node)
    return None
