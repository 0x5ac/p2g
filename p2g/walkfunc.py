import ast
import dataclasses
import itertools
import typing

from p2g import err
from p2g import gbl
from p2g import op
from p2g import sys
from p2g import walkbase
from p2g import walkexpr
from p2g import walkstat


# unique type to compare
Marker = gbl.sentinel()
# look through caller's args and insert defaults
# etc. to be compatible with callee, return dict
# with mapping.


def formal_kwargs(formalspec, formals, kwargs, pos) -> dict[str, typing.Any]:

    # Process incoming keyword arguments, putting them in namespace if
    # actual arg exists by that name, or offload to function's kwarg
    # if any. All make needed checks and error out.
    func_kwarg = {}
    final_dict = {}
    all_formals = {
        x.arg
        for x in itertools.chain(formals.args, formals.kwonlyargs, formals.kw_defaults)
        if x is not None
    }
    for key, value in kwargs.items():
        if key in all_formals:
            final_dict[key] = value
        elif formalspec.kwarg:
            func_kwarg[key] = value
        else:
            err.compiler("Bad arguments.", node=pos)
    if formalspec.kwarg:
        final_dict[formalspec.kwarg.arg] = func_kwarg
    return final_dict


def check_missing(final_dict, formalspec, pos):
    # check for missing args
    for formal in itertools.chain(formalspec.args, formalspec.kwonlyargs):
        if formal.arg not in final_dict:
            err.compiler(f"Missing argument '{formal.arg}'.", node=pos)


def get_defaults(walker, formals):
    first_defaulted = len(formals.args) - len(formals.defaults)
    return {
        # position args defaults
        el.arg: walker.visit(formals.defaults[idx - first_defaulted])
        for idx, el in enumerate(formals.args)
        if idx >= first_defaulted
    } | {
        # kwargs defaults
        el.arg: walker.visit(val)
        for el, val in zip(formals.kwonlyargs, formals.kw_defaults)
        if val is not None
    }


def gather_func_formals(func_def, *args, **kwargs):
    walker = func_def.walker
    formals = func_def.node.args
    # report error in caller rather than definition.

    pos = gbl.iface.last_node
    final_dict = {}
    formalspec = func_def.node.args
    if formalspec.vararg:
        final_dict[formalspec.vararg.arg] = args[len(formalspec.args):]
    else:
        if len(args) > len(formalspec.args):
            err.compiler(
                f"Too many arguments; {len (args)} > {len(formalspec.args)}.", node=pos
            )
    for argidx in range(min(len(args), len(formalspec.args))):
        final_dict[formalspec.args[argidx].arg] = args[argidx]
    # result contains at least the defaults.
    final_dict |= get_defaults(walker, formals)
    final_dict |= formal_kwargs(formalspec, formals, kwargs, pos)
    check_missing(final_dict, formalspec, pos)
    return final_dict


# calling a function, emit code to call, and
# generate the called code.  And save it, to make
# sure that other generations make the same.
def inline(func_def, *args, **kwargs):

    walker = func_def.walker

    prev_file = walker.file_name
    prev_func = walker.func_name
    walker.file_name = func_def.file_name
    walker.func_name = func_def.func_name

    # We need to switch from dynamic execution scope to lexical scope
    # in which function was defined (then switch back on return).
    dyna_scope = walker.ns

    with walker.pushpopns(func_def.lexical_scope):
        assert walker.ns == func_def.lexical_scope
        res = None
        with walker.pushpop_funcns():
            formals_dict = gather_func_formals(func_def, *args, **kwargs)
            walker.ns.guts.update(formals_dict)
            res = walker.visit_slist(func_def.node.body)

    assert walker.ns == dyna_scope
    walker.func_name = prev_func
    walker.file_name = prev_file
    return res


@dataclasses.dataclass
class FuncDefWrap:
    file_name: str
    func_name: str
    node: ast.AST
    walker: "WalkFunc"
    lexical_scope: walkbase.Namespace

    def __init__(self, walker, node):
        self.func_name = node.name
        self.file_name = walker.module_ns["__file__"]
        self.node = node
        self.walker = walker
        self.lexical_scope = walker.ns

    def __call__(self, *args, **kwargs):
        return inline(self, *args, **kwargs)


def interpfunc(fun):
    def func(*args, **kwargs):
        if args and isinstance(args[0], Marker):
            return fun

        return fun(*args, **kwargs)

    return func


@dataclasses.dataclass
class FuncArgsDescr:
    args: list[typing.Any]
    kwargs: dict[str, typing.Any]

    def __init__(self, walker, node):
        args = []
        for arg in node.args:
            if isinstance(arg, ast.Starred):
                args.extend(walker.visit(arg.value))
            else:
                args.append(walker.visit(arg))
        kwargs = {}
        for keyword in node.keywords:
            val = walker.visit(keyword.value)
            if keyword.arg is None:
                kwargs.update(val)
            else:
                kwargs[keyword.arg] = val
        self.args = args
        self.kwargs = kwargs


def funcall(target, *args, **kwargs):
    return target(*args, **kwargs)


class WalkFunc(walkbase.WalkBase):
    def _visit_call(self, node):
        defn = self.visit(node.func)
        if defn.__module__ == "p2g.sys" and defn.__name__ == "print":
            with sys.BSS():
                # keep bss so 'stack' used gathering dprint arguments
                # gets returned.
                desc = FuncArgsDescr(self, node)
                return funcall(defn, *desc.args, **desc.kwargs)

        desc = FuncArgsDescr(self, node)

        if defn.__module__ == "p2g.builtin":
            return op.make_scalar_func(defn.__name__, *desc.args)
        return funcall(defn, *desc.args, **desc.kwargs)

    def _visit_functiondef(self, node):
        desc = FuncDefWrap(self, node)
        ifunc = interpfunc(desc)
        self.ns[node.name] = ifunc


class Walk(
    walkstat.WalkStatement,
    walkexpr.WalkExpr,
    walkbase.WalkNS,
    WalkFunc,
    walkbase.WalkBase,
):
    pass
