# magic for things like
#  a) g.goto.fast ([1,2])
#  b) foo = g.probe.slow
#  c)foo(z=12)


import dataclasses
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


def unpack(args, kwargs) -> vector.RValueVec:
    resmap: typing.Dict[int, scalar.Scalar] = {}
    if args:
        args = map(vector.wrap_maybe_vec, args)
        args = flatten(args)

        for idx, value in enumerate(args):
            resmap[idx] = value

    # can have x=1,y=1 or xy=(somthing)
    for axis_string, values in kwargs.items():
        values = vector.wrap_maybe_vec(values)
        axis_indexes = axis.name_to_indexes_list(axis_string)
        for axis_idx, value in zip(axis_indexes, values.forever()):
            if axis_idx in resmap:
                err.compiler(f"Overlapping axes {args} {kwargs}")
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
    return vector.RValueVec(
        [resmap.get(x) for x in range(max(min_size, coord_size))], from_user=True
    )


# build things like AABuilder(1,2,3, _addr=123) and AABuilder[8](_addr=123)
@dataclasses.dataclass
class _TypeBuilder:
    btype: str
    size: int

    def __init__(self, btype="c", *, size=None):
        self.btype = btype
        self.size = size

    def check_addr_sanity(self, addr):
        if addr is None:
            return
        if self.btype == "c":
            err.compiler("Const can't have an address.")
        elif self.btype == "a":
            err.compiler("Var can't have an address.")

    def check_size_sanity(self, size, initialized_size):
        if initialized_size > 0 and initialized_size != size:
            err.compiler(f"Conflicting sizes {self.size} and {initialized_size}")
        if size == 0 and initialized_size == 0:
            err.compiler("Zero sized vector.")

    def workout_size(self, initialized_size):
        size = self.size
        if size is None:
            size = max(initialized_size, 1)
        self.check_size_sanity(size, initialized_size)
        return size

    def __call__(
        self,
        *args,
        addr=None,
        **kwargs,
    ):
        self.check_addr_sanity(addr)
        values = unpack(args, kwargs)

        initialized_size = values.nelements()

        size = self.workout_size(initialized_size)

        if self.btype == "c":
            return values
        if addr is None:
            addr = gbl.iface.next_bss(size)
        res = vector.MemVec(addr, size)
        if values.nelements():
            for lhs, rhs in zip(res.everything(), values.forever()):
                stat.append_set(lhs, rhs)

        return res

    # sets vector size.
    def __getitem__(self, el):
        return _TypeBuilder(
            size=el,
            btype=self.btype,
        )


Var = _TypeBuilder("a")
Fixed = _TypeBuilder("f")
Const = _TypeBuilder("c")
