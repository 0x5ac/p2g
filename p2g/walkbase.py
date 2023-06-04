import ast
import contextlib
import typing

from typing import Any

from p2g import err
from p2g import stat
from p2g import walkns


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
    ns: "walkns.ANamespace"
    module_ns: "walkns.ModuleNS"
    file_name: str
    func_name: str

    def __init__(self):
        self.file_name = ""
        self.func_name = ""

        self.module_ns = walkns.ModuleNS()
        self.ns = self.module_ns
        self.loop = typing.cast(LoopContext, None)
        self.module_ns = typing.cast(walkns.ModuleNS, None)

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
        err.compiler(f"{name} not implemented")

    def _visit_return(self, node):
        if not isinstance(self.ns, walkns.FunctionNS):  # hard to test right
            err.compiler("'return' outside function")
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

    @contextlib.contextmanager
    def pushpopns(self, ns):
        ns.parent = self.ns
        self.ns = ns
        yield
        self.ns = self.ns.parent

    def _visit_expr(self, node):
        self.visit(node.value)


class WalkNS(WalkBase):
    def _visit_global(self, node):
        for n in node.names:
            if n in self.ns and self.ns[n] is not walkns.GLOBAL:  # hard to test right
                err.compiler(f"Name {n} before global")
            # Don't store GLOBAL in the top-level namespace
            if self.ns.parent:
                self.ns[n] = walkns.GLOBAL

    def _visit_nonlocal(self, node):
        if isinstance(self.ns, walkns.ModuleNS):  # hard to test right
            err.compiler("nonlocal declaration not allowed at module level")
        for n in node.names:
            self.ns[n] = walkns.NONLOCAL
