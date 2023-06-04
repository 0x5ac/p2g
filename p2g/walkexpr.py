import ast

from p2g import op
from p2g import walkbase
from p2g import walkns


def enumerate_comps(self, iters):
    def eval_ifs(its):
        for cond in its.ifs:
            if not self.visit(cond):
                return False
        return True

    if not iters:
        yield
        return
    for el in self.visit(iters[0].iter):
        self.visit_store(iters[0].target, el)
        for _ in enumerate_comps(self, iters[1:]):
            if eval_ifs(iters[0]):
                yield


class WalkExpr(walkbase.WalkBase):
    def _visit_listcomp(self, node):
        with self.pushpopns(walkns.FunctionNS()):
            return [self.visit(node.elt) for _ in enumerate_comps(self, node.generators)]

    def _visit_setcomp(self, node):
        with self.pushpopns(walkns.FunctionNS()):
            return {self.visit(node.elt) for _ in enumerate_comps(self, node.generators)}

    def _visit_dictcomp(self, node):
        with self.pushpopns(walkns.FunctionNS()):
            return {
                self.visit(node.key): self.visit(node.value)
                for _ in enumerate_comps(self, node.generators)
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
        res = []

        for value in node.values:
            match value:
                case ast.Constant():
                    res.append(value.value)
                case ast.FormattedValue():
                    val = self.visit(value.value)

                    if value.format_spec is not None:
                        # turn python format into g-code
                        fmt = self.visit(value.format_spec)
                        el = op.make_fmt(val, fmt)
                    else:
                        el = op.make_fmt(val, "")
                    res.append(el)

        return "".join(res)

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
                return getattr(obj, node.attr)
        return None

    def _visit_store_attribute(self, node, store_val):
        setattr(self.visit(node.value), node.attr, store_val)

    def _visit_name(self, node):
        return walkns.handle_visit_name(self, node)

    def _visit_store_name(self, node, store_val):
        return walkns.handle_visit_name_store(self, node, store_val)

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
