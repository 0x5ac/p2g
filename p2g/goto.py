# noqa: V841
# noqa: V841i
# noqa: V102
# noqa: V103
# noqa: V101
# noqa: V105
import dataclasses
import enum

from p2g import axis
from p2g import coords
from p2g import err
from p2g import nd
from p2g import stat


class MovementSpace(enum.IntEnum):
    UNDEFINED = enum.auto()
    RELATIVE = enum.auto()
    WORK = enum.auto()
    MACHINE = enum.auto()
    R9810 = enum.auto()

    def __str__(self):
        return self.name.lower()


class MovementOrder(enum.IntEnum):
    UNDEFINED = enum.auto()
    XYZ = enum.auto()
    Z_LAST = enum.auto()
    Z_FIRST = enum.auto()

    def __str__(self):
        return self.name.lower()


@dataclasses.dataclass(eq=True, frozen=True)
class GotoWorker:
    _space: MovementSpace
    _order: MovementOrder
    _feed: float
    _probe: bool
    _mcode: str

    def accumulate_coords(self, cos):
        for aname, value in cos:
            yield f"{aname}{value.to_gcode(nd.NodeModifier.EMPTY)}"

    def accumulate_probe(self):
        if self._probe:
            yield "G31 G55"
        else:
            yield "G01 G55"

    def accumulate_mcode(self):
        if self._mcode:
            yield self._mcode

    def accumulate_feed(self):
        if self._feed == 0.0:
            err.compiler("Need feed rate.")
        yield f"F{nd.to_gcode(self._feed)}"

    def update(self, key, value):
        xxx = {**self.__dict__, key: value}
        return GotoWorker(**xxx)

    def _update_space(self, newv):
        if self._space not in (MovementSpace.UNDEFINED, newv):
            err.compiler(f"Conflicting spaces for goto, '{self._space}' and '{newv}'.")
        return self.update("_space", newv)

    def _update_order(self, newv):
        if self._order not in (MovementOrder.UNDEFINED, newv):
            err.compiler(f"Conflicting orders for goto, '{self._order}' and '{newv}'.")
        return self.update("_order", newv)

    @property  # noqa
    def relative(self):
        return self._update_space(MovementSpace.RELATIVE)

    @property  # noqa
    def work(self):
        return self._update_space(MovementSpace.WORK)  # noqa: V841

    @property  # noqa
    def r9810(self):
        return self._update_space(MovementSpace.R9810)

    @property  # noqa
    def machine(self):
        return self._update_space(MovementSpace.MACHINE)

    @property  # noqa
    def z_first(self):
        return self._update_order(MovementOrder.Z_FIRST)

    @property  # noqa
    def z_last(self):
        return self._update_order(MovementOrder.Z_LAST)

    @property  # noqa
    def all(self):
        return self._update_order(MovementOrder.XYZ)

    @property  # noqa
    def xyz(self):
        return self._update_order(MovementOrder.XYZ)

    @property  # noqa
    def probe(self):
        return self.update("_probe", True)

    def feed(self, _feed):  # noqa
        return self.update("_feed", _feed)

    def mcode(self, m_code):  # noqa
        return self.update("_mcode", str(m_code))

    def accumulate_parts1(self):
        match self._space:
            case MovementSpace.RELATIVE:
                yield "G91"
                yield from self.accumulate_probe()
                yield from self.accumulate_mcode()
            case MovementSpace.MACHINE:
                yield "G90"
                yield "G53"
                yield from self.accumulate_probe()
                yield from self.accumulate_mcode()
            case MovementSpace.WORK:
                yield "G90"
                yield from self.accumulate_probe()
                yield from self.accumulate_mcode()
            case MovementSpace.R9810:
                yield "G65 R9810"
                if self._probe:
                    err.compiler("Probe with 9810 move is illegal.")
                if self._mcode:
                    err.compiler("MCODE with 9810 move is illegal.")
            case _:
                err.compiler(
                    "'goto' needs one of 'relative','machine', 'work' or 'R9810'."
                )
        yield from self.accumulate_feed()

    def do_goto_worker(self, fter, args, kwargs):
        # split out arguments we understand from
        # ones for coordinates.
        def get_coords():
            values = coords.unpack(args, kwargs)
            for aname, value in zip(axis.low_names_v(), values):
                # skip non mentioned coords
                if fter != "*" and aname not in fter:
                    continue
                # skip non there coords
                if value.is_none_constant:
                    continue
                yield aname, value

        cos = list(get_coords())
        if not cos:
            return

        stat.code(
            self.accumulate_parts1(),
            self.accumulate_coords(cos),
        )

    def __call__(self, *args, **kwargs):
        match self._order:
            case MovementOrder.UNDEFINED:
                err.compiler("'goto' needs movement order, 'all', 'z_first' or 'z_last'.")
            case MovementOrder.XYZ:
                self.do_goto_worker("*", args, kwargs)
            case MovementOrder.Z_FIRST:
                self.do_goto_worker("z", args, kwargs)
                self.do_goto_worker("xyabc", args, kwargs)
            case MovementOrder.Z_LAST:
                self.do_goto_worker("xyabc", args, kwargs)
                self.do_goto_worker("z", args, kwargs)

    def __repr__(self):
        return (
            f"goto space={self._space} order={self._order.value} "
            f"_feed={self._feed} probe={self._probe} mcode='{self._mcode}'"
        )


goto = GotoWorker(
    _space=MovementSpace.UNDEFINED,
    _order=MovementOrder.UNDEFINED,
    _feed=0,
    _probe=False,
    _mcode="",
)
