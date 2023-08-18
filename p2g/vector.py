# noqa
import abc
import typing

from p2g import axis
from p2g import err
from p2g import nd
from p2g import scalar
from p2g import stat
from p2g import symbol


class Vec(nd.EBase, nd.FakeOps):
    def __init__(self):
        pass

    def __div__(self, other):
        pass  # no cover

    def __mult__(self, other):
        pass  # no cover

    @abc.abstractmethod
    def nelements(self) -> int:
        ...

    @abc.abstractmethod
    def get_address(self) -> scalar.Scalar:
        ...

    @abc.abstractmethod
    def get_at(self, idx: scalar.Scalar) -> scalar.Scalar:
        ...

    @abc.abstractmethod
    def get_slice(self, slindex: slice) -> "Vec":
        ...

    def to_scalar(self):
        return self[0]

    def get_axes_vec(self, key):
        if key == "var":
            return TupleV(list(scalar.urange(0, self.nelements())))
        indexes = axis.name_to_indexes_list(key)
        if max(indexes) >= self.nelements():
            err.compiler("Reference to too many axes.")
        return TupleV(indexes)

    def forever(self) -> typing.Generator[scalar.Scalar, None, None]:
        while True:
            yield from self.everything()

    def __getattr__(self, key):
        if key[0] == "_":
            return object.__getattribute__(self, key)
        axes_vec = self.get_axes_vec(key)
        return sorv_from_list([self.get_at(idx) for idx in axes_vec])

    def __setattr__(self, key, value):
        if key[0] == "_":
            object.__setattr__(self, key, value)
            return
        value = wrap(value)
        axes_vec = self.get_axes_vec(key)
        for idx, src in zip(axes_vec, value.forever()):
            self.set_at(idx, src)

    def __getitem__(self, scalar_index) -> scalar.Scalar:
        if isinstance(scalar_index, slice):
            return typing.cast(scalar.Scalar, self.get_slice(scalar_index))
        return self.get_at(scalar.wrap_scalar(scalar_index))


class TupleV(Vec):
    _guts: list[scalar.Scalar]
    _from_user: bool

    def __init__(self, value, from_user=False):
        super().__init__()
        object.__setattr__(self, "_guts", [])
        object.__setattr__(self, "_from_user", from_user)
        for el in value:
            self._guts.append(scalar.wrap_scalar(el))

    def __div__(self, _other):
        return self  # no cover

    def get_address(self):
        return self._guts[0].get_address()

    def everything(self) -> typing.Generator[scalar.Scalar, None, None]:
        yield from self._guts

    def get_at(self, idx: scalar.Scalar) -> scalar.Scalar:
        return self._guts[int(idx)]

    def nelements(self) -> int:
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
        return symbol.Group.USER, ",".join(res)

    def get_slice(self, slindex: slice):
        return TupleV(self._guts[slindex])

    def __iter__(self):
        yield from self._guts

    def __str__(self):  # no cover
        return ", ".join(map(str, self._guts))


symbol.HasToSymTabEntry.register(TupleV)
# stub overwritten by op.py to avoid cycles


def local_hashop(_addr: scalar.Scalar, _idx: scalar.Scalar) -> scalar.Scalar:
    raise NotImplementedError


class MemVec(Vec):
    _size: scalar.Scalar
    _addr: scalar.Scalar
    _step: scalar.Scalar

    def __init__(self, _addr=0, _size=0, _step=1):
        super().__init__()
        self._addr = scalar.wrap_scalar(_addr)
        self._size = scalar.wrap_scalar(_size)
        self._step = scalar.wrap_scalar(_step)

    def __div__(self, _other):
        return self  # no cover

    def get_address(self):
        return self._addr

    def to_symtab_entry(self, varrefs) -> typing.Tuple[symbol.Group, str]:
        fwidth = 7
        hit_indexes: dict[int, bool] = {}
        for el, addr in enumerate(scalar.urange(self._addr, self._addr + self._size)):
            if addr in varrefs:
                hit_indexes[el] = True

        if hit_indexes and max(hit_indexes) >= len(axis.NAMES):
            return symbol.Group.VECTOR, f"#{self._addr}[{self._size}]".rjust(fwidth)
        res = []
        for idx in scalar.urange(0, self._size):
            if idx not in hit_indexes:
                continue
            res.append(
                f"#{self._addr + idx}.{axis.low_names(idx)}".rjust(fwidth),
            )
        return symbol.Group.VECTOR, " ".join(res)

    def nelements(self) -> int:
        return int(self._size)

    def everything(self) -> typing.Generator[scalar.Scalar, None, None]:
        return (
            self.get_at(scalar.wrap_scalar(idx))
            for idx in scalar.urange(0, self._size, int(self._step))
        )

    def get_at(self, idx: scalar.Scalar):
        res = local_hashop(self._addr, idx)
        if not isinstance(idx, scalar.Constant):
            return res
        fidx = int(idx)
        if not 0 <= fidx < int(self._size):
            err.compiler(
                f"Index out of range, index={fidx} size={self._size}.",
            )
        return res

    def set_at(self, idx: scalar.Scalar, src: scalar.Scalar):
        if src.is_none_constant:
            return
        stat.append_set(self.get_at(idx), src)

    def get_slice(self, slindex: slice):
        tmp = (list(range(self.nelements())))[slindex]
        step = 0
        if len(tmp) > 1:
            step = tmp[1] - tmp[0]
        addr = self._addr + tmp[0]
        size = tmp[-1] - tmp[0] + 1
        assert addr is not None
        return MemVec(addr, size, step)

    def __setitem__(self, indexes, src):
        if isinstance(indexes, slice):
            indexes = list(range(*indexes.indices(self.nelements())))
        indexes = wrap(indexes)
        src = wrap(src)
        for idx, sel in zip(indexes.everything(), src.forever()):
            stat.append_set(self[idx], sel)

    def __repr__(self):
        return f"(array {self._addr} {self._size})"


def wrap(thing) -> typing.Union[Vec, scalar.Scalar]:
    if isinstance(thing, (TupleV, MemVec)):
        return thing
    if isinstance(thing, (list, set, dict)):
        return TupleV(thing)
    if isinstance(thing, tuple):
        return TupleV(list(thing))
    return scalar.wrap_scalar(thing)


def wrap_mustbe_vector(src):
    if isinstance(src, Vec):
        return src

    raise err.CompilerError("Only vectors have addresses.")


symbol.HasToSymTabEntry.register(MemVec)


def sorv_from_list(thing: list) -> typing.Union[Vec, scalar.Scalar]:
    if len(thing) != 1:
        return TupleV(thing)
    return thing[0]
