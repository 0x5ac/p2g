import abc
import enum


class NodeModifier(enum.IntFlag):
    # so 0 is an error
    EMPTY = enum.auto()

    # ADDRESSES are always integers
    ADDRESS = enum.auto()
    ARGUMENT = enum.auto()
    NOSPACE = enum.auto()
    # TAKES UP 7 spaces.
    F3X3 = enum.auto()


class HasToSymTab(abc.ABC):
    user_defined = False

    @abc.abstractmethod
    def to_symtab_entry(self, _addrs_used) -> str:
        return ""


# common base class for scalar and vector.
class EBase(abc.ABC):
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
