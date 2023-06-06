import abc
import ast
import math
import typing

from p2g import err
from p2g import gbl
from p2g import lib
from p2g import nd
from p2g import opinfo
from p2g import scalar
from p2g import vector


OptRes = typing.Optional[scalar.Scalar]

op_byclass: typing.Dict[typing.Any, opinfo.Opinfo] = {}
allops: typing.Dict[str, opinfo.Opinfo] = {}


def parensif(cond, thing):
    if cond:
        return "[" + thing + "]"
    return thing


def get_prec(thing):
    return getattr(thing, "prec", 20)


class Binop(scalar.Scalar):
    def __init__(self, opfo, lhs, rhs):
        super().__init__(opfo)
        assert opfo.pyn != "-rev"
        self.lhs = lhs
        self.rhs = rhs

    def same(self, other):
        return (
            self.opfo == other.opfo
            and lib.same(self.lhs, other.lhs)
            and lib.same(self.rhs, other.rhs)
        )

    def to_gcode(self, modi: nd.NodeModifier) -> str:
        if self.opfo.g_func:
            res = [
                nd.to_gcode(self.lhs, modi),
                nd.to_gcode(self.rhs, modi),
            ]
            return f"{self.opfo.gname}[{','.join(res)}]"

        res = []

        outer_prec = self.opfo.prec

        def handle_term(node):
            return parensif(
                get_prec(node) < outer_prec,
                nd.to_gcode(node, modi),
            )

        res.append(handle_term(self.lhs))
        res.append(self.opfo.gname)
        res.append(handle_term(self.rhs))

        if modi & nd.NodeModifier.NOSPACE:
            return "".join(res)
        return " ".join(res)

    def __repr__(self):
        return f"({self.lhs}{self.opfo.pyn}{self.rhs})"


def make_scalar_binop(opfo, lhs, rhs):
    # can it be done right now?
    if isinstance(rhs, scalar.ConstantNone):
        rhs = scalar.wrap_scalar(0)
    if isinstance(lhs, scalar.Constant) and isinstance(rhs, scalar.Constant):
        lval = lhs.value
        rval = rhs.value
        if isinstance(lval, float) or isinstance(rval, float):
            lval = float(lval)
            rval = float(rval)
        if opfo.pyn == "round":
            rval = int(rval)
        res = getattr(lval, opfo.mth)(rval)
        return scalar.Constant(res)
    # put contant on rhs if we can
    if (
        opfo.comm
        and isinstance(lhs, scalar.Constant)
        and not isinstance(rhs, scalar.Constant)
    ):
        lhs, rhs = rhs, lhs

    if opfo.opt2 and (res := opfo.opt2(opfo, lhs, rhs)) is not None:
        return res

    return Binop(opfo, lhs, rhs)


def make_scalar_add(lhs, rhs):
    return make_scalar_binop(allops["+"], lhs, rhs)


def a2opfo(optyp):
    return op_byclass[optyp]


def opt1_func(opfo, arg) -> OptRes:
    if not isinstance(arg, scalar.Constant):
        return None

    return scalar.wrap_scalar(opfo.lam(arg.to_float()))


class Unop(scalar.Scalar):
    def __init__(self, opfo, child):
        super().__init__(opfo)
        self.child = child

    def get_address(self):
        return self.child

    def same(self, other):
        return self.opfo == other.opfo and lib.same(self.child, other.child)

    def to_gcode(self, modifier=nd.NodeModifier.EMPTY):
        res = []

        if self.opfo.pyn == "#":
            gbl.iface.add_varref(self.child, err.state.last_pos)

        outer_prec = self.opfo.prec

        res.append(self.opfo.gname)
        # at least # is left right associative.
        inside_prec = get_prec(self.child)

        if self.opfo.pyn == "#":
            modifier |= nd.NodeModifier.ADDRESS

        res.append(
            parensif(
                outer_prec >= inside_prec,
                nd.to_gcode(self.child, modifier),
            )
        )

        return "".join(res)

    def __repr__(self):
        return f"({self.opfo.pyn} {self.child})"


def make_scalar_unop(opfo, child: scalar.Scalar):
    child = scalar.wrap_scalar(child)
    if opfo.opt1 and (res := opfo.opt1(opfo, child)) is not None:
        return res

    if isinstance(child, scalar.Constant):
        return scalar.wrap_scalar(getattr(child.value, opfo.mth)())

    return Unop(opfo, child)


def make_vec_binop(opfo, lhs, rhs=None, force_ourtype=False):
    if not force_ourtype and not isinstance(lhs, (int, float, nd.EBase)):
        return getattr(lhs, opfo.mth)(rhs)

    lhs = vector.wrap_maybe_vec(lhs)

    if rhs is None:
        # actually unop.

        return vector.sorv_from_list(
            [make_scalar_unop(opfo, el) for el in lhs.everything()]
        )
    rhs = vector.wrap_maybe_vec(rhs)
    return vector.sorv_from_list(
        [
            make_scalar_binop(opfo, lel, rel)
            for lel, rel in zip(lhs.everything(), rhs.forever())
        ]
    )


def make_scalar_func(fname, *args):
    ofo = allops[fname]
    return make_vec_binop(ofo, args[0], force_ourtype=True)


class MAST(abc.ABC):
    opfo: opinfo.Opinfo


MAST.register(ast.AST)


class HASH(MAST):
    pass


class ABS(MAST):
    pass


class RSUB(MAST):
    pass


class ROUND(MAST):
    pass


revop = {
    "+": "+",
    "-": "+",
    "*": "*",
    "/": "*",
}


# a  + k1  + k2 -> a + (k1+k2)
def opt2_fold(opfo, lhs, rhs) -> OptRes:
    rop = revop.get(opfo.pyn)

    if (
        rop
        and isinstance(lhs, Binop)
        and lhs.opfo == opfo
        and lhs.rhs.is_constant
        and rhs.is_constant
    ):
        return make_scalar_binop(
            opfo,
            lhs.lhs,
            make_scalar_binop(
                allops[rop],
                lhs.rhs,
                rhs,
            ),
        )

    return None


def opt2_mul(opfo, lhs, rhs) -> OptRes:
    match rhs.to_float():
        case 0.0:
            return scalar.Constant(0.0)
        case 1.0:
            return lhs
        case -1.0:
            return make_scalar_unop(allops["un-"], lhs)

    return opt2_fold(opfo, lhs, rhs)


def opt2_div(opfo, lhs, rhs) -> OptRes:
    match rhs.to_float():
        case None:
            return None
        case 0.0:
            err.compiler("Attempt to divide by zero.")
        case 1.0:
            return lhs
        case -1.0:
            return make_scalar_unop(allops["un-"], lhs)

    return opt2_fold(opfo, lhs, rhs)


not_compop = {
    "==": "!=",
    "!=": "==",
    "<": ">=",
    ">": "<=",
    "<=": ">",
    ">=": "<",
}


def opt1_not(_opinfo, arg) -> OptRes:
    if arg.is_constant:
        return scalar.Constant(not arg.value)

    # got not(comop, turn into (inverted compop))

    if notted := not_compop.get(arg.opfo.pyn):
        return make_scalar_binop(allops[notted], arg.lhs, arg.rhs)

    rhs = scalar.Constant(0)
    return make_scalar_binop(allops["!="], arg, rhs)


def opt1_plus(_, arg) -> OptRes:
    return arg


# don't have binary not operator, make from xor.
def opt1_invert(_, arg) -> OptRes:
    rhs = scalar.wrap_scalar(-1)
    return make_scalar_binop(allops["^"], arg, rhs)


# turn a1 > a2  == 0
# => (a1 <= a2)


def opt2_eq(opfo, lhs: scalar.Scalar, rhs: scalar.Scalar) -> OptRes:
    if lib.same(lhs, rhs):
        return scalar.Constant(opfo.pyn == "==")

    if not isinstance(rhs, scalar.Constant) or rhs.value != 0.0:
        return None

    if isinstance(lhs, Binop):
        if rev := not_compop.get(lhs.opfo.pyn):
            if opfo.pyn == "==":
                return make_scalar_binop(
                    allops[rev],
                    lhs.lhs,
                    lhs.rhs,
                )
            return lhs
    return None


def opt2_matmul(_opfo, _lhs, _rhs) -> OptRes:  # for debug
    return None


def opt2_add(opfo, lhs, rhs) -> OptRes:
    if (res := opt2_fold(opfo, lhs, rhs)) is not None:
        return res

    if isinstance(rhs, Unop) and rhs.opfo.pyn == "un-":
        return make_scalar_binop(allops["-"], lhs, rhs.child)

    if isinstance(rhs, scalar.Constant):
        rhsv = rhs.to_float()
        if rhsv < 0.0:
            return make_scalar_binop(allops["-"], lhs, -rhsv)
        if rhsv == 0.0:
            return lhs

    return None


def make_fmt(val, fmt):
    if isinstance(val, str):
        return val
    val = scalar.wrap_scalar(val)
    if isinstance(val, scalar.Constant):
        if fmt and fmt[-1] == "x":
            return format(val.to_int(), fmt)
        return format(val.to_float(), fmt)
    gfmt = f"[{fmt[0]}{fmt[2]}]" if fmt else ""

    return "[" + val.to_gcode(nd.NodeModifier.NOSPACE) + "]" + gfmt


def opt2_sub(opfo, lhs, rhs) -> OptRes:
    if (res := opt2_fold(opfo, lhs, rhs)) is not None:
        return res

    # a -  - b -> a + b
    if isinstance(rhs, Unop) and rhs.opfo.pyn == "un-":
        return make_scalar_binop(allops["+"], lhs, rhs.child)

    if isinstance(rhs, scalar.Constant):
        rhsv = rhs.to_float()
        if rhsv == 0.0:
            return lhs

    return None


def unwrap_int(val):
    try:
        return val.to_int()
    except AttributeError:
        return val


def make_slice(low, high, step):
    return slice(
        unwrap_int(low),
        unwrap_int(high),
        unwrap_int(step),
    )


def hashop(arg):
    return Unop(allops["#"], arg)


def make_hashop(lhs, rhs):
    return hashop(make_scalar_add(lhs, rhs))


vector.MemVec.make_hashop = make_hashop


def opinfo_install(opfo: opinfo.Opinfo):
    def make_multi_binop_tramp(lhs, rhs):
        return make_vec_binop(opfo, lhs, rhs)

    def make_multi_unop_tramp(child):
        return vector.sorv_from_list(
            [make_scalar_unop(opfo, cel) for cel in child.everything()]
        )

    def make_scalar_binop_tramp(lhs, rhs):
        return make_scalar_binop(opfo, lhs, scalar.wrap_scalar(rhs))

    def make_scalar_unop_tramp(child):
        return make_scalar_unop(opfo, child)

    if opfo.mth:
        if isinstance(opfo.mth, str):
            if opfo.nargs == 1:
                setattr(vector.Vec, opfo.mth, make_multi_unop_tramp)
                setattr(scalar.Scalar, opfo.mth, make_scalar_unop_tramp)
            else:
                setattr(vector.Vec, opfo.mth, make_multi_binop_tramp)
                setattr(scalar.Scalar, opfo.mth, make_scalar_binop_tramp)


def reg(**kwargs):
    opi = opinfo.Opinfo(**kwargs)
    allops[opi.pyn] = opi
    op_byclass[opi.astc] = opi
    opinfo_install(opi)


def regfunc(name, lam):
    reg(
        pyn=name,
        lam=lam,
        gname=name.upper(),
        prec=20,
        nargs=1,
        opt1=opt1_func,
    )


regfunc("cos", lambda x: math.cos(math.radians(x)))
regfunc("sin", lambda x: math.sin(math.radians(x)))
regfunc("tan", lambda x: math.tan(math.radians(x)))
regfunc("acos", lambda x: math.degrees(math.acos(x)))
regfunc("asin", lambda x: math.degrees(math.asin(x)))
regfunc("atan", lambda x: math.degrees(math.atan(x)))
regfunc("exp", math.exp)
regfunc("ln", math.log)
regfunc("sqrt", math.sqrt)
regfunc("exists", id)
regfunc("fup", math.ceil)
regfunc("fix", math.floor)
regfunc("ground", round)


# fmt: off
# noqa: E203
reg(astc=ast.BitOr    , pyn="|"     , mth="__or__"       , gname="OR"    , prec=4, comm=True)
reg(astc=ast.BitXor   , pyn="^"     , mth="__xor__"      , gname="XOR"   , prec=5, comm=True)
reg(astc=ast.BitAnd   , pyn="&"     , mth="__and__"      , gname="AND"   , prec=6, comm=True)
reg(astc=ast.Lt       , pyn="<"     , mth="__lt__"       , gname="LT"    , prec=10)
reg(astc=ast.LtE      , pyn="<="    , mth="__le__"       , gname="LE"    , prec=10)
reg(astc=ast.NotEq    , pyn="!="    , mth="__ne__"       , gname="NE"    , prec=10, comm=True, opt2=opt2_eq)
reg(astc=ast.Eq       , pyn="=="    , mth="__eq__"       , gname="EQ"    , prec=10, comm=True, opt2=opt2_eq)
reg(astc=ast.Gt       , pyn=">"     , mth="__gt__"       , gname="GT"    , prec=10)
reg(astc=ast.GtE      , pyn=">="    , mth="__ge__"       , gname="GE"    , prec=10)
reg(astc=ast.Sub      , pyn="-"     , mth="__sub__"      , gname="-"     , prec=12, opt2=opt2_sub)
reg(astc=None         , pyn="-rev"  , mth="__rsub__"     , gname="-rev"  , prec=12)
reg(astc=ast.Add      , pyn="+"     , mth="__add__"      , gname="+"     , prec=12, comm=True, opt2=opt2_add)
reg(astc=None         , pyn="round" , mth="__round__"    , gname="round" , prec=12)
reg(astc=ast.Mult     , pyn="*"     , mth="__mul__"      , gname="*"     , prec=13, comm=True, opt2=opt2_mul)
reg(astc=ast.Div      , pyn="/"     , mth="__truediv__"  , gname="/"     , prec=13, opt2=opt2_div)
reg(astc=ast.FloorDiv , pyn="//"    , mth="__floordiv__" , gname="//"    , prec=13, opt2=opt2_div)
reg(astc=ast.Mod      , pyn="%"     , mth="__mod__"      , gname="MOD"   , prec=14)
reg(astc=ast.Pow      , pyn="**"    , mth="__pow__"      , gname="POW"   , prec=15, g_func=True)
reg(astc=ast.USub     , pyn="un-"   , mth="__neg__"      , gname="-"     , prec=14, nargs=1)
reg(astc=ast.UAdd     , pyn="un+"   , mth="__pos__"      , gname="+"     , prec=14, nargs=1, opt1=opt1_plus)
reg(astc=ast.MatMult  , pyn="m*"    , mth=""             , gname="ERRR"  , prec=20, nargs=2, opt2=opt2_matmul)
reg(astc=ast.Invert   , pyn="un~"   , mth="__invert__"   , gname="un~"   , prec=14, nargs=1, opt1=opt1_invert)
reg(astc=ast.Not      , pyn="unot"  , mth=""             , gname="unot"  , prec=14, nargs=1, opt1=opt1_not)
reg(astc=None         , pyn="abs"   , mth="__abs__"      , gname="ABS"   , prec=15, nargs=1, g_func=True)
reg(astc=None         , pyn="#"     , mth=""             , gname="#"     , prec=19, nargs=1)


# fmt:on
