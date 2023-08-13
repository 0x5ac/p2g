import copy
import enum
import typing

from p2g import axis
from p2g import err
from p2g import gbl
from p2g import scalar
from p2g import stat
from p2g import vector


def flatten(args):
    res = []
    for el in args:
        for subel in el.everything():
            res.append(subel)
    return res


def unpack(args, kwargs) -> vector.TupleV:
    resmap: typing.Dict[int, scalar.Scalar] = {}
    if args:
        args = map(vector.wrap, args)
        args = flatten(args)
        for idx, value in enumerate(args):
            resmap[idx] = value
    # can have x=1,y=1 or xy=(somthing)
    for axis_string, values in kwargs.items():
        values = vector.wrap(values)
        axis_indexes = axis.name_to_indexes_list(axis_string)
        for axis_idx, value in zip(axis_indexes, values.forever()):
            if axis_idx in resmap:
                err.compiler(f"Overlapping axes {args} {kwargs}.")
            resmap[axis_idx] = value
    # fill any holes.
    coord_size = 0
    if resmap:
        coord_size = max(resmap) + 1
    # rules:
    # everything in the input gets packed into
    # the output in the right order.
    # if something is a nan in the input, and
    # we've got gap_default, then the nan is
    # turned into that.
    min_size = 0
    return vector.TupleV(
        [resmap.get(x) for x in range(max(min_size, coord_size))], from_user=True
    )


class CoNum(enum.IntEnum):
    CONST = enum.auto()
    FIXED = enum.auto()
    VAR = enum.auto()


# build things like AABuilder(1,2,3, _addr=123) and AABuilder[8](_addr=123)
class CoType:
    size: typing.Optional[int]
    cot: CoNum
    # for typing, default works too.
    x: "CoType"

    def __init__(self, cot: CoNum):
        self.cot = cot
        self.size = None

    def check_size_sanity(self, size, initialized_size):
        if initialized_size > 0 and initialized_size != size:
            raise err.CompilerError(
                f"Conflicting sizes {self.size} and {initialized_size}."
            )
        if size == 0 and initialized_size == 0:
            err.compiler("Zero sized vector.")

    def workout_size(self, initialized_size):
        size = self.size
        if size is None:
            size = max(initialized_size, 1)
        self.check_size_sanity(size, initialized_size)
        return size

    def __call__(self, *args, addr: typing.Optional[int] = None, **kwargs):
        values = unpack(args, kwargs)
        initialized_size = values.nelements()
        size = self.workout_size(initialized_size)
        match self.cot:
            case CoNum.CONST:
                if addr is not None:
                    raise err.CompilerError("Const can't have an address.")
                return values
            case CoNum.FIXED:
                if addr is None:
                    raise err.CompilerError("Fixed needs an address.")
            case CoNum.VAR:
                if addr is not None:
                    raise err.CompilerError("Var can't have an address.")
                addr = gbl.iface.next_bss(size)
            case _:  # no cover
                raise NotImplementedError
        res = vector.MemVec(addr, size)
        if initialized_size:
            for lhs, rhs in zip(res.everything(), values.forever()):
                stat.append_set(lhs, rhs)
        return res

    # sets vector size.
    def __getitem__(self, el):
        cop = copy.copy(self)
        cop.size = el
        return cop


Var = CoType(CoNum.VAR)
Fixed = CoType(CoNum.FIXED)
Const = CoType(CoNum.CONST)
