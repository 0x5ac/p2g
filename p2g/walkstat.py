import ast
import dataclasses

from p2g import coords
from p2g import err
from p2g import nd
from p2g import op
from p2g import scalar
from p2g import stat
from p2g import vector
from p2g import walkbase


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
    src_gen = iter(val)  # pytype: disable=wrong-arg-types
    try:
        for dst_idx, dst_el in enumerate(target.elts):
            if isinstance(dst_el, ast.Starred):
                src_togo = list(src_gen)
                break_i = len(src_togo) - (len(target.elts) - dst_idx - 1)
                self.visit_store(dst_el.value, src_togo[:break_i])
                src_gen = iter(src_togo[break_i:])
            else:
                self.visit_store(dst_el, next(src_gen))
    except StopIteration:
        err.compiler("Not enough values to unpack.")
    ensure_no_more(src_gen)


# make code for while and for loops.
@dataclasses.dataclass
class ItrRange:
    target: ast.AST

    def __init__(self, itr, interp, target):
        self.interp = interp
        self.rang = itr
        self.var = coords.Var()
        if not isinstance(target, ast.Name):
            err.compiler("Must be simple name as destination for 'for'.")
        self.var = coords.Var()
        interp.ns[target.id] = self.var

    #        interp.ns[target.id] = self.var
    def setup_index(self):
        pass

    def setup_target(self):
        stat.add_stat(
            stat.Set(scalar.wrap_scalar(self.var), scalar.wrap_scalar(self.rang.start))
        )

    def cur_index(self):
        return self.var

    def past_index(self):
        return self.rang.stop

    def load_target(self):
        pass

    def next_index(self):
        stat.add_stat(
            stat.Set(
                scalar.wrap_scalar(self.var),
                op.make_scalar_add(scalar.wrap_scalar(self.var), self.rang.step),
                comment_txt=stat.CommentGen.NONE,
            )
        )


@dataclasses.dataclass
class ItrSlice:
    ptr: nd.EBase
    pastptr: scalar.Scalar
    step: scalar.Scalar
    var: ast.AST

    def __init__(self, itr, interp, target):
        self.interp = interp
        self.target = target
        # with a slice, always need a pointer to
        # look at things.
        # scalar.wrap_scalar(coords.Var(itr._addr))
        self.ptr = coords.Var(itr._addr)
        if not isinstance(target, ast.Name):
            err.compiler("Must be simple name as destination for 'for'.")
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
        handle_assign(self.interp, self.target, op.hashop(scalar.wrap_scalar(self.ptr)))

    def next_index(self):
        stat.add_stat(
            stat.Set(
                scalar.wrap_scalar(self.ptr),
                op.make_scalar_add(scalar.wrap_scalar(self.ptr), self.step),
                comment_txt=stat.CommentGen.NONE,
            )
        )


def make_itr(itr, interp, target):
    if isinstance(itr, vector.Vec):
        return ItrSlice(itr, interp, target)
    if isinstance(itr, range):
        return ItrRange(itr, interp, target)
    raise err.CompilerError("Illegal iterator.")


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
        stat.add_stat(
            stat.Goto(
                self.loop.lcontinue,
            ),
        )
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
        stat.add_stat(
            stat.Goto(
                self.loop.lcontinue,
            ),
        )
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
        self.ns = self.module_ns = walkbase.Namespace()
        self.ns["__file__"] = file_name
        self.file_name = file_name
        self.ns["__name__"] = "__main__"
        self.visit_slist(node.body)

    def visit_module(self, node, file_name):
        self._visit_module(node, file_name)

    def _visit_classdef(self, node):
        with self.pushpop_classns() as ns:
            self.visit_slist(node.body)
            guts = ns.guts
        cls = type(node.name, tuple(self.visit(b) for b in node.bases), guts)
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

    def _visit_with(self, node):
        ctxes = [self.visit(el.context_expr) for el in node.items]
        entry_vals = (ctx.__enter__() for ctx in ctxes)
        for el, val in zip(node.items, entry_vals):
            if var := el.optional_vars:
                handle_assign(self, var, val)
        self.visit_slist(node.body)
        for ctx in reversed(ctxes):
            ctx.__exit__(None, None, None)

    def _visit_if(self, node):
        #   for nicer looking code
        # for a conditional break.
        if isinstance(node.body[0], ast.Break):
            exp = op.make_scalar_unop(op.a2opfo(ast.UAdd), self.visit(node.test))
            self.loop.lbreak.used = True
            stat.add_stat(stat.If(exp, self.loop.lbreak))
            return
        elsepart = stat.next_label()
        donepart = stat.next_label()
        cond = op.make_scalar_unop(op.a2opfo(ast.UAdd), self.visit(node.test))
        # nice code for if with constant.
        if cond.is_constant:
            if cond:
                self.visit_slist(node.body)
            else:
                self.visit_slist(node.orelse)
        else:
            exp1 = op.make_scalar_unop(op.a2opfo(ast.Not), cond)
            stat.add_stat(stat.If(exp1, on_t=elsepart))
            self.visit_slist(node.body)
            stat.add_stat(
                stat.Goto(
                    donepart,
                ),
            )
            stat.add_stat(
                stat.LabelDef(
                    elsepart,
                ),
            )
            self.visit_slist(node.orelse)
            stat.add_stat(
                stat.LabelDef(
                    donepart,
                ),
            )

    def _visit_import(self, node):
        for name in node.names:
            self.ns[name.asname or name.name] = __import__(name.name)

    def _visit_importfrom(self, node):
        mod = __import__(
            node.module, None, None, [n.name for n in node.names], node.level
        )
        for name in node.names:
            if name.name == "*":
                for modname, modguts in mod.__dict__.items():
                    if modname[0] != "_":
                        self.ns[modname] = modguts
            else:
                self.ns[name.asname or name.name] = getattr(mod, name.name)

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
        for dst in node.targets:
            handle_assign(self, dst, val)

    def _visit_delete(self, node):
        for dst in node.targets:
            self.visit(dst)

    def _visit_pass(self, _):
        pass

    # assert turns into if with alarm.
    def _visit_assert(self, node):
        assert_ok = scalar.wrap_scalar(self.visit(node.test))
        msg_txt = self.visit(node.msg)
        ass_stat = stat.Set(
            scalar.wrap_scalar(3001),
            scalar.Constant(100),
            msg_txt=msg_txt,
        )
        if assert_ok.is_constant:
            if assert_ok:
                stat.add_stat(stat.Code(["( ok )"]))
                return
            stat.add_stat(ass_stat)
            return
        ifexp = op.make_scalar_unop(op.a2opfo(ast.Not), assert_ok)
        stat.add_stat(stat.IfSet(ifexp, ass_stat))
