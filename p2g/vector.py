import typing

from p2g import axis
from p2g import err
from p2g import nd
from p2g import scalar
from p2g import stat


class Vec(nd.EBase):
    is_scalar = False
    is_vec = True

    _assoc_name: str
    _read: bool

    def __init__(self):
        self._read = False
        self._assoc_name = ""

    def to_scalar(self):
        return self[0]

    def get_axes_vec(self, key):
        if key == "var":
            return RValueVec(list(scalar.urange(0, self.nelements())))

        indexes = axis.name_to_indexes_list(key)
        if max(indexes) >= self.nelements():
            err.compiler("Reference to too many axes.")
        return RValueVec(indexes)

    def forever(self):
        self._read = True
        while True:
            yield from self.everything()

    def __getattr__(self, key):
        if key[0] == "_":
            return getattr(self, key)

        axes_vec = self.get_axes_vec(key)

        return sorv_from_list([self.get_at(idx) for idx in axes_vec])

    def __setattr__(self, key, value):
        if key[0] == "_":
            object.__setattr__(self, key, value)
            return
        value = wrap_maybe_vec(value)
        axes_vec = self.get_axes_vec(key)

        for idx, src in zip(axes_vec, value.forever()):
            self.set_at(idx, src)

    def __getitem__(self, scalar_index):
        if isinstance(scalar_index, slice):
            return self.get_slice(scalar_index)
        return self.get_at(scalar.wrap_scalar(scalar_index))

    def __add__(self, _other) -> "Vec":  # placeholder, filled in from op.reg
        return self

    def __mul__(self, _other) -> "Vec":  # placeholder, filled in from op.reg
        return self


class RValueVec(Vec):
    _guts: list[scalar.Scalar]
    _from_user: bool

    # def __eq_(self, a):
    #     breakpoint()

    def __init__(self, value, from_user=False):
        super().__init__()

        object.__setattr__(self, "_guts", [])

        object.__setattr__(self, "_from_user", from_user)
        for el in value:
            self._guts.append(scalar.wrap_scalar(el))

    @property
    def user_defined(self):
        return self._from_user

    def get_address(self):
        return self._guts[0].get_address()

    def everything(self):
        self._read = True
        return self._guts

    def get_at(self, idx: scalar.Scalar):
        self._read = True
        return self._guts[int(idx)]

    def nelements(self):
        return len(self._guts)

    def to_symtab_entry(self, _):
        res = []
        tlen = 0
        for el in self._guts:
            nextstr = nd.to_gcode(el, nd.NodeModifier.F3X3)
            tlen += len(nextstr)
            if tlen > 21:
                res.append("...")
                break
            res.append(nextstr)

        return ",".join(res)

    def __iter__(self):
        yield from self._guts

    def __str__(self):
        return ", ".join(map(str, self._guts))


class MemVec(Vec):
    # nasty fix forward ref
    make_hashop: typing.Callable

    _size: scalar.Scalar
    _addr: scalar.Scalar
    _step: scalar.Scalar

    # $    def __eq__(self, x):
    #        breakpoint()
    #    def __hash__(self):
    #        return 1

    def __init__(self, _addr=0, _size=0, _step=1):
        super().__init__()
        self._addr = scalar.wrap_scalar(_addr)
        self._size = scalar.wrap_scalar(_size)
        self._step = scalar.wrap_scalar(_step)

    @property
    def user_defined(self):
        return True

    def get_address(self):
        return self._addr

    def to_symtab_entry(self, varrefs):
        fwidth = 7
        hit_indexes = {}

        for el, addr in enumerate(scalar.urange(self._addr, self._addr + self._size)):
            if addr in varrefs:
                hit_indexes[el] = True

        if hit_indexes and max(hit_indexes) >= len(axis.NAMES):
            return f"#{self._addr}[{self._size}]".rjust(fwidth)
        res = []

        for idx in scalar.urange(0, self._size):
            if idx not in hit_indexes:
                continue

            res.append(
                f"#{self._addr + idx}.{axis.low_names(idx)}".rjust(fwidth),
            )
        return " ".join(res)

    def nelements(self):
        return int(self._size)

    def everything(self):
        return (
            self.get_at(scalar.wrap_scalar(idx))
            for idx in scalar.urange(0, self._size, self._step)
        )

    def get_at(self, idx: scalar.Scalar):
        if isinstance(idx, scalar.Constant):
            fidx = int(idx)
            if not 0 <= fidx < int(self._size):
                err.compiler(
                    f"Index out of range, index={fidx} size={self._size}",
                )

        return MemVec.make_hashop(idx, self._addr)

    def set_at(self, idx: scalar.Scalar, src: scalar.Scalar):
        stat.append_set(self.get_at(idx), src)

    def get_slice(self, index: slice):
        tmp = (list(range(self.nelements())))[index]
        step = 0
        if len(tmp) > 1:
            step = tmp[1] - tmp[0]

        return MemVec(self._addr + tmp[0], tmp[-1] - tmp[0] + 1, step)

    def __setitem__(self, indexes, src):
        if isinstance(indexes, slice):
            indexes = list(range(*indexes.indices(self.nelements())))
        indexes = wrap_maybe_vec(indexes)
        src = wrap_maybe_vec(src)
        for idx, sel in zip(indexes.everything(), src.forever()):
            stat.append_set(self[idx], sel)

    def __repr__(self):
        return f"(array  {self._addr} {self._size})"


def wrap_optional_maybe_vec(
    thing,
) -> typing.Optional[typing.Union[Vec, scalar.Scalar]]:
    if (res := scalar.wrap_optional_scalar(thing)) is not None:
        return res

    if isinstance(thing, list):
        return RValueVec(thing)
    if isinstance(thing, (RValueVec, MemVec)):
        return thing
    if isinstance(thing, (set, dict)):
        return RValueVec(thing)
    if isinstance(thing, tuple):
        return RValueVec(list(thing))

    raise AssertionError


def wrap_maybe_vec(thing) -> typing.Union[Vec, scalar.Scalar]:
    res = wrap_optional_maybe_vec(thing)
    assert res is not None
    return res


def sorv_from_list(thing: list) -> typing.Union[Vec, scalar.Scalar]:
    if len(thing) != 1:
        return RValueVec(thing)
    return thing[0]
