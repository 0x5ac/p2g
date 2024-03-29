import ast

from p2g import fstring
from p2g import op
from p2g import symbol
from p2g import walkbase


class WalkExpr(walkbase.WalkBase):
    def _eval_ifs(self, its):
        for cond in its.ifs:
            if not self.visit(cond):
                return False
        return True

    def _enumerate_comps(self, iters):
        if iters:
            for el in self.visit(iters[0].iter):
                self.visit_store(iters[0].target, el)
                for _ in self._enumerate_comps(iters[1:]):
                    if self._eval_ifs(iters[0]):
                        yield
        else:
            yield

    def _visit_listcomp(self, node):
        with self.pushpop_funcns():
            return [self.visit(node.elt) for _ in self._enumerate_comps(node.generators)]

    def _visit_setcomp(self, node):
        with self.pushpop_funcns():
            return {self.visit(node.elt) for _ in self._enumerate_comps(node.generators)}

    def _visit_dictcomp(self, node):
        with self.pushpop_funcns():
            return {
                self.visit(node.key): self.visit(node.value)
                for _ in self._enumerate_comps(node.generators)
            }

    def _visit_ifexp(self, node):
        # turn x if tst else y
        # into   x * (tst ) + (y *  (1-tst))
        lhs = self.visit(node.body)
        rhs = self.visit(node.orelse)
        cond = self.visit(node.test)
        cond = cond != 0
        not_cond = cond == 0
        return lhs * cond + rhs * not_cond

    def _visit_compare(self, node):
        acc = self.visit(node.left)
        for cop, child in zip(node.ops, node.comparators):
            acc = op.make_vec_binop(op.a2opfo(type(cop)), acc, self.visit(child))
        return acc

    def _visit_boolop(self, node):
        if isinstance(node.op, ast.And):
            res = True
            for val in node.values:
                res = res and self.visit(val)
        else:
            res = False
            for val in node.values:
                res = res or self.visit(val)
        return res

    def _visit_joinedstr(self, node):
        return fstring.joinedstr(self, node)

    def _visit_binop(self, node):
        return op.make_vec_binop(
            op.a2opfo(type(node.op)),
            self.visit(node.left),
            self.visit(node.right),
        )

    def _visit_unaryop(self, node):
        return op.make_vec_binop(
            op.a2opfo(type(node.op)),
            self.visit(node.operand),
        )

    def _visit_subscript(self, node):
        obj = self.visit(node.value)
        idx = self.visit(node.slice)
        match node.ctx:
            case ast.Del():
                del obj[idx]
            case _:
                return obj[idx]
        return None

    def _visit_store_subscript(self, node, store_val):
        self.visit(node.value)[self.visit(node.slice)] = store_val

    def _visit_slice(self, node):
        return op.make_slice(
            self.visit(node.lower), self.visit(node.upper), self.visit(node.step)
        )

    def _visit_attribute(self, node):
        obj = self.visit(node.value)
        match node.ctx:
            case ast.Del():
                delattr(obj, node.attr)
            case _:
                res = getattr(obj, node.attr)
                symbol.Table.remember_load(node.attr, res)
                return res
        return None

    def _visit_store_attribute(self, node, store_val):
        symbol.Table.remember_store(node.attr, store_val)
        setattr(self.visit(node.value), node.attr, store_val)

    def _visit_name(self, node):
        return walkbase.handle_visit_name(self, node)

    def _visit_store_name(self, node, store_val):
        return walkbase.handle_visit_name_store(self, node, store_val)

    def _visit_dict(self, node):
        return {self.visit(p[0]): self.visit(p[1]) for p in zip(node.keys, node.values)}

    def _visit_set(self, node):
        return {self.visit(e) for e in node.elts}

    def _visit_list(self, node):
        return [self.visit(e) for e in node.elts]

    def _visit_tuple(self, node):
        return tuple(self.visit(e) for e in node.elts)

    def _visit_constant(self, node):
        return node.value
