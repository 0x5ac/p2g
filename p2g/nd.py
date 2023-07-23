# just information about operators.
import abc
import ast
import enum
import typing


def opt_null(*_):
    return None


class Opinfo(typing.NamedTuple):
    astc: typing.Optional[typing.Type] = None
    pyn: str = ""
    mth: str = ""
    lam: typing.Callable = opt_null
    gname: str = ""
    prec: int = 20
    comm: bool = False
    nargs: int = 2
    g_func: bool = False
    opt: typing.Callable = opt_null

    # def rtl_get_arg_(self, _idx):
    #     return self.pyn

    # def rtl_arg_info_(self):
    #     return ["opinfo"]


const_nd = Opinfo(astc=ast.Constant, pyn="konstant", gname="", prec=20)


class NodeModifier(enum.IntFlag):
    # so 0 is an error
    EMPTY = enum.auto()
    # ADDRESSES are always integers
    ADDRESS = enum.auto()
    ARGUMENT = enum.auto()
    NOSPACE = enum.auto()
    # TAKES UP 7 spaces.
    F3X3 = enum.auto()


# operators are generated mechanically, but these
# are for typing hints:
class FakeOps:
    def __div__(self, _other):
        return self  # no cover

    def __add__(self, _other):
        return self  # no cover

    def __sub__(self, _other):
        return self  # no cover

    def __mul__(self, _other):
        return self  # no cover

    def __floordiv__(self, _other):
        return self  # no cover

    def __neg__(self):
        return self  # no cover

    def __abs__(self):
        return self  # no cover

    def __lt__(self, _other):
        return self  # no cover

    def __gt__(self, _other):
        return self  # no cover


def to_rtl(self):
    name = self.__class__.__name__

    ainfo = self.rtl_arg_info_()
    yield "(" + name + " "
    assert isinstance(ainfo, list)
    for idx, info in enumerate(ainfo):
        yield info
        arg = self.rtl_get_arg_(idx)
        match info:
            case "constant":
                yield str(arg)
            case "?string":
                yield str(arg)
            case "labeldef":
                yield str(arg)
            case "labelref":
                yield str(arg)

            case "opfo":
                yield str(arg.pyn)
            case _:
                yield from to_rtl(arg)
    yield ")"


# common base class for scalar and vector.
class EBase(abc.ABC, FakeOps):
    @abc.abstractmethod
    def everything(self) -> typing.Generator[typing.Any, None, None]:
        ...

    def get_address(self):
        raise NotImplementedError

    def set_at(self, _idx, _src):
        raise NotImplementedError

    # def rtl_arg_info_(self):
    #     return [f"-exp-null-{self.__class__.__name__}"]

    # def rtl_get_arg_(self, _idx):
    #     return Null()


# class Null(EBase):
#     def everything(self) -> typing.Generator[typing.Any, None, None]:
#         raise IndexError

#     def rtl_arg_info_(self):

#         return []

#     def rtl_get_arg_(self, idx):
#         raise IndexError


DECIMALS = 4


def to_gcode_from_float(thing, modifier=NodeModifier.EMPTY):
    if modifier & NodeModifier.ADDRESS:
        return str(int(thing))
    if modifier & NodeModifier.F3X3:
        return f"{thing:7.3f}"
    res = str(round(float(thing), DECIMALS))
    if res.endswith(".0"):
        res = res[:-1]
    return res


def to_gcode(thing, modifier=NodeModifier.EMPTY) -> str:
    if isinstance(thing, (float, int)):
        return to_gcode_from_float(thing, modifier)
    return thing.to_gcode(modifier)
