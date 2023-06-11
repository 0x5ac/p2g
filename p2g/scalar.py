import abc
import typing

from p2g import nd
from p2g import opinfo


Ctype = typing.Union[float, int, str]


class Scalar(nd.EBase):
    opfo: opinfo.Opinfo
    is_none_constant = False
    is_constant = False
    is_string_constant = False
    is_numeric_constant = False
    is_scalar = True

    def __init__(self, opfo):
        self.opfo = opfo

    @property
    def prec(self):
        return self.opfo.prec

    def get_address(self):
        return None

    def forever(self):
        while True:
            yield self

    def to_float(self):
        return None

    def everything(self):
        yield self

    # placeholder to east typechecking,
    # overwitten by op install machines.
    @abc.abstractmethod
    def __add__(self, _other):
        pass

    @abc.abstractmethod
    def __lt__(self, _other):
        pass

    def __int__(self) -> int:
        raise TypeError


class ConstantBase(Scalar):
    is_constant = True


class Constant(ConstantBase):
    _value: int | float
    is_numeric_constant = True

    def __init__(self, value: int | float):
        super().__init__(opinfo.const_opinfo)
        self._value = value

    @property
    def value(self):
        return self._value

    def same(self, other: "Constant"):
        return isinstance(other, Constant) and other.value == self._value

    def to_int(self) -> int:
        return int(self)

    def to_float(self):
        return float(self._value)

    def to_gcode(self, modifier=nd.NodeModifier.EMPTY) -> str:
        return nd.to_gcode_from_float(self._value, modifier)

    def __bool__(self):
        if self._value:
            return True

        return False

    def __int__(self) -> int:
        return int(self._value)

    def __repr__(self):
        return f"<{self._value}>"

    def __str__(self):
        return str(self._value)


class ConstantNone(ConstantBase):
    is_none_constant = True

    def __init__(self):
        super().__init__(opinfo.const_opinfo)


class ConstantStr(ConstantBase):
    value: str
    is_string_constant = True

    def __init__(self, value: str):
        super().__init__(opinfo.const_opinfo)
        self.value = value

    def to_gcode(self, modifier=nd.NodeModifier.EMPTY) -> str:
        # as an integer literal or as a string.

        if modifier & nd.NodeModifier.ARGUMENT:
            return f"{ord(self.value)}."
        return f"'{self.value}'"


def wrap_optional_scalar(thing) -> typing.Optional[Scalar]:
    if isinstance(thing, str):
        return ConstantStr(thing)

    if isinstance(thing, (int, float, bool)):
        return Constant(thing)
    if isinstance(thing, Scalar):
        return thing
    return None


def wrap_scalar(thing) -> Scalar:
    if thing is None:
        return ConstantNone()
    res = wrap_optional_scalar(thing)
    if res is not None:
        return res

    return thing.to_scalar()


# make a range between wrapped items and yield ints
def urange(start, stop, step=1):
    stop = int(stop)
    step = int(step)

    tmp = list(range(int(start), stop, step))
    for el in tmp:
        yield el
