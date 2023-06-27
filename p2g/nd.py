import abc
import ast

# just information about operators.
# pylint: disable=too-many-instance-attributes
import dataclasses
import enum
import typing


def opt_null(*_):
    return None


@dataclasses.dataclass(kw_only=True)
class Opinfo:
    astc: typing.Optional[typing.Type] = None
    pyn: str = ""
    mth: str = ""
    lam: typing.Callable = opt_null
    gname: str = ""
    prec: int = 20
    comm: bool = False
    nargs: int = 2
    g_func: bool = False

    opt1: typing.Callable = opt_null
    opt2: typing.Callable = opt_null


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


# common base class for scalar and vector.
class EBase(abc.ABC):
    @abc.abstractmethod
    def everything(self) -> typing.Generator[typing.Any, None, None]:
        ...

    def get_at(self, _idx) -> typing.Any:
        return None  # no cover

    def set_at(self, _idx, _src):
        pass  # no cover

    def nelements(self):
        return 1  # no cover

    def get_slice(self, _slice) -> typing.Any:
        return None  # no cover

    @abc.abstractmethod
    def get_address(self) -> int:
        ...

    def to_gcode(self, _modifier: NodeModifier) -> str:
        return ""  # no cover

    # placeholder to east typechecking,
    # overwitten by op install machines.
    @abc.abstractmethod
    def __add__(self, _other):
        pass

    @abc.abstractmethod
    def __lt__(self, _other):
        pass


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
