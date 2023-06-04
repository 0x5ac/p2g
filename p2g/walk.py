import abc
import ast
import dataclasses
import pathlib
import re
import sys

from loguru import logger

from p2g import axis
from p2g import coords
from p2g import err
from p2g import gbl
from p2g import lib
from p2g import op
from p2g import scalar
from p2g import stat
from p2g import vector
from p2g import walkbase
from p2g import walkexpr
from p2g import walkfunc
from p2g import walkns


# wrap enough state that we can call an
# ast function as if it were native.


def ensure_no_more(src_gen):
    try:
        next(src_gen)
        err.compiler("Too many values to unpack.")

    except StopIteration:
        pass


def handle_assign(self, target, val):
    if not isinstance(target, ast.Tuple):
        self.visit_store(target, val)
        return

    src_gen = iter(val)
    try:
        for dst_idx, dst_el in enumerate(target.elts):
            if isinstance(dst_el, ast.Starred):
                src_togo = list(src_gen)
                break_i = len(src_togo) - (len(target.elts) - dst_idx - 1)
                self.visit_store(dst_el.value, src_togo[:break_i])
                src_gen = iter(src_togo[break_i:])
            else:
                self.visit_store(dst_el, next(src_gen))

    except StopIteration as exc:
        err.compiler("Not enough values to unpack.", exc)

    ensure_no_more(src_gen)


# make code for while and for loops.


class Itr(abc.ABC):
    @abc.abstractmethod
    def __init__(self, itr, target):
        pass

    @abc.abstractmethod
    def cur_index(self):
        pass

    @abc.abstractmethod
    def last_index(self):
        pass

    @abc.abstractmethod
    def next_target(self):
        pass

    @abc.abstractmethod
    def next_index(self):
        pass


@dataclasses.dataclass
class ItrRange:
    target: ast.AST

    def __init__(self, itr, interp, target):
        self.interp = interp
        self.rang = itr
        self.var = coords.Var()

        if not isinstance(target, ast.Name):
            err.compiler("must be simple name as destination for for")
        self.var = coords.Var()
        interp.ns[target.id] = self.var

    #        interp.ns[target.id] = self.var

    def setup_index(self):
        pass

    def setup_target(self):
        stat.add_stat(
            stat.Set(
                scalar.wrap_scalar(self.var),
                scalar.wrap_scalar(self.rang.start),
            )
        )

    #        breakpoint()
    #        handle_assign(self.interp, self.var, self.rang.start)

    def cur_index(self):
        return self.var

    def past_index(self):
        return self.rang.stop

    def load_target(self):
        pass

    def next_index(self):
        # stat.add_stat(
        #     stat.Set(
        #         scalar.wrap_scalar(self.target),
        #         op.make_scalar_add(scalar.wrap_scalar(self.target), self.step),
        #     )
        # )

        stat.add_stat(
            stat.Set(
                scalar.wrap_scalar(self.var),
                op.make_scalar_add(scalar.wrap_scalar(self.var), self.rang.step),
            )
        )


@dataclasses.dataclass
class ItrSlice:
    ptr: scalar.Scalar
    pastptr: scalar.Scalar
    step: scalar.Scalar
    var: ast.AST

    def __init__(self, itr, interp, target):
        self.interp = interp
        #        breakpoint()
        self.target = target

        # with a slice, always need a pointer to
        # look at things.
        self.ptr = coords.Var(itr._addr)  # scalar.wrap_scalar(coords.Var(itr._addr))

        if not isinstance(target, ast.Name):
            err.compiler("must be simple name as destination for for")

        self.pastptr = itr._addr + itr._size
        self.step = itr._step

    def setup_index(self):
        pass

    def setup_target(self):
        pass

    def cur_index(self):
        return self.ptr

    def past_index(self):
        return self.pastptr

    def load_target(self):
        #        breakpoint()
        handle_assign(self.interp, self.target, op.hashop(scalar.wrap_scalar(self.ptr)))

    #        stat.add_stat(stat.Set(self.interp.visit(self.var), op.hashop(self.ptr)))

    def next_index(self):
        stat.add_stat(
            stat.Set(
                scalar.wrap_scalar(self.ptr),
                op.make_scalar_add(scalar.wrap_scalar(self.ptr), self.step),
            )
        )


def make_itr(itr, interp, target):
    if isinstance(itr, vector.Vec):
        return ItrSlice(itr, interp, target)
    if isinstance(itr, range):
        return ItrRange(itr, interp, target)

    err.compiler("Illegal iterator.")


def geniter(
    self,
    *,
    whileexp=None,
    target=None,
    itr=None,
    body=None,
    orelse=None,
):
    self.loop = walkbase.LoopContext(self.loop)

    if whileexp:
        stat.add_stat(stat.LabelDef(self.loop.lcontinue))
        test = op.make_scalar_unop(op.a2opfo(ast.Not), self.visit(whileexp))
        stat.add_stat(stat.If(test, self.loop.lorelse))
        self.visit_slist(body)
        stat.add_stat(stat.Goto(self.loop.lcontinue))
    else:
        assert itr

        itr = make_itr(itr, self, target)

        itr.setup_index()
        itr.setup_target()
        stat.add_stat(stat.LabelDef(self.loop.lcontinue))

        stat.add_stat(
            stat.If(
                op.make_vec_binop(
                    op.a2opfo(ast.GtE),
                    itr.cur_index(),
                    itr.past_index(),
                ),
                self.loop.lorelse,
            )
        )
        itr.load_target()
        self.visit_slist(body)
        itr.next_index()
        stat.add_stat(stat.Goto(self.loop.lcontinue))

    if orelse:
        stat.add_stat(stat.LabelDef(self.loop.lorelse))
        self.visit_slist(orelse)
        if self.loop.lbreak.used:
            stat.add_stat(stat.LabelDef(self.loop.lbreak))
    else:
        if self.loop.lbreak.used:
            stat.add_stat(stat.LabelDef(self.loop.lbreak))
        stat.add_stat(stat.LabelDef(self.loop.lorelse))
    self.loop = self.loop.prev


class WalkStatement(walkbase.WalkBase):
    def wrap_decorators(self, obj, node):
        for deco_n in reversed(node.decorator_list):
            deco = self.visit(deco_n)
            obj = deco(obj)
        return obj

    def _visit_module(self, node, file_name):
        self.ns = self.module_ns = walkns.ModuleNS()
        self.ns["__file__"] = file_name
        self.file_name = file_name
        self.ns["__name__"] = "__main__"

        self.visit_slist(node.body)

    def visit_module(self, node, file_name):
        self._visit_module(node, file_name)

    def _visit_classdef(self, node):
        clsns = walkns.ClassNS()
        with self.pushpopns(clsns):
            self.visit_slist(node.body)

        cls = type(
            node.name,
            tuple(self.visit(b) for b in node.bases),
            clsns.guts,
        )
        cls = self.wrap_decorators(cls, node)
        self.ns[node.name] = cls

    def _visit_for(self, node):
        itr = self.visit(node.iter)
        return geniter(
            self, target=node.target, itr=itr, body=node.body, orelse=node.orelse
        )

    def _visit_while(self, node):
        geniter(self, whileexp=node.test, body=node.body, orelse=node.orelse)

    def _visit_break(self, _):
        self.loop.lbreak.used = True
        stat.add_stat(stat.Goto(self.loop.lbreak))

    def _visit_continue(self, _):
        stat.add_stat(stat.Goto(self.loop.lcontinue))

    def _visit_if(self, node):
        #   for nicer looking code
        if isinstance(node.body[0], ast.Break):
            exp = op.make_scalar_unop(op.a2opfo(ast.UAdd), self.visit(node.test))
            self.loop.lbreak.used = True
            stat.add_stat(stat.If(exp, self.loop.lbreak))
            return

        elsepart = stat.next_label()
        donepart = stat.next_label()
        exp1 = op.make_scalar_unop(op.a2opfo(ast.Not), self.visit(node.test))
        stat.add_stat(stat.If(exp1, on_t=elsepart))
        self.visit_slist(node.body)
        stat.add_stat(stat.Goto(donepart))
        stat.add_stat(stat.LabelDef(elsepart))
        self.visit_slist(node.orelse)
        stat.add_stat(stat.LabelDef(donepart))

    def _visit_import(self, node):
        for n in node.names:
            self.ns[n.asname or n.name] = __import__(n.name)

    def _visit_importfrom(self, node):
        mod = __import__(
            node.module, None, None, [n.name for n in node.names], node.level
        )

        for n in node.names:
            if n.name == "*":
                for modname, modguts in mod.__dict__.items():
                    if modname[0] != "_":
                        self.ns[modname] = modguts
            else:
                self.ns[n.asname or n.name] = getattr(mod, n.name)

    def _visit_augassign(self, node):
        self.visit_store(
            node.target,
            op.make_vec_binop(
                op.a2opfo(type(node.op)),
                self.visit(node.target),
                self.visit(node.value),
            ),
        )

    def _visit_annassign(self, node):
        if node.value is not None:
            val = self.visit(node.value)
            handle_assign(self, node.target, val)

    def _visit_assign(self, node):
        val = self.visit(node.value)
        for n in node.targets:
            handle_assign(self, n, val)

    def _visit_delete(self, node):
        for n in node.targets:
            self.visit(n)

    def _visit_pass(self, _):
        pass

    def _visit_assert(self, node):
        res = self.visit(node.test)
        if node.msg is None:
            if not res:
                assert res
        else:
            assert res, self.visit(node.msg)


class Walk(
    WalkStatement,
    walkexpr.WalkExpr,
    walkbase.WalkNS,
    walkfunc.WalkFunc,
    walkbase.WalkBase,
):
    pass


def compile_all(node, srcfile_name):
    walker = Walk()
    walker.visit_module(node, srcfile_name)
    return walker


def find_main_func_name(sourcelines, func_name_arg):
    if func_name_arg != "<last function in file>":
        return func_name_arg
    function_to_call = ""
    for line in sourcelines.split("\n"):
        # find last line with def in it, that's the function we need
        mares = re.match("(.*)def (.*?)\\(", line)
        if mares:
            function_to_call = mares.group(2)
    return function_to_call


@lib.g2l
def compile2g(func_name_arg, srcfile_name, job_name, in_pytest):
    gbl.config.in_pytest = in_pytest

    srcpath = pathlib.Path(srcfile_name)

    with lib.openr(srcpath) as inf:
        sys.path.insert(0, str(srcpath.parent))

        with stat.Nest(in_pytest) as cursor:
            axis.NAMES = "xyz"
            gbl.iface.reset()

            logger.debug(f"Starting {func_name_arg} {cursor.next_label}")
            sourcelines = inf.read()
            node = ast.parse(sourcelines)
            # load everything

            walker = compile_all(node, srcfile_name)
            if node.body:
                walkfunc.digest_top(
                    walker,
                    find_main_func_name(sourcelines, func_name_arg),
                    srcpath,
                    job_name,
                )
            res = cursor.to_full_lines()
            return res


class WantInline:
    def __init__(self, fn):
        self.fn = fn


# at definition of an inline function,
# just remember the tree.
def inline(fn):
    return WantInline(fn)
