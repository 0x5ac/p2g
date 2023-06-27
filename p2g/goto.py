import dataclasses
import enum

from p2g import axis
from p2g import coords
from p2g import err
from p2g import gbl
from p2g import nd
from p2g import stat


# fast and slow and neither look up params.
# can be changed by using explicit feed.
# kwargs could contain x,y,z,feed ec
# as could extras


class MovementSpace(enum.IntEnum):
    WORK = enum.auto()
    MACHINE = enum.auto()
    R9810 = enum.auto()


class MovementRelOrAbs(enum.IntEnum):
    RELATIVE = enum.auto()
    ABSOLUTE = enum.auto()


class MovementOrder(enum.IntEnum):
    XYZ = enum.auto()
    XY_THEN_Z = enum.auto()
    Z_THEN_XY = enum.auto()


def do_goto_worker(self, fter, args, kwargs):
    # split out arguments we understand from
    # ones for coordinates.

    def accumulate_relorabs():
        match self.relorabs_:
            case MovementRelOrAbs.ABSOLUTE:
                yield "G90"

            case MovementRelOrAbs.RELATIVE:
                yield "G91"

    def accumulate_probe():
        if self.probe_:
            yield "G31"

    def accumulate_mcode():
        if self.mcode_:
            yield self.mcode_

    def accumulate_feed():
        if self.feed_ == 0.0:
            err.compiler("Need feed rate.")

        yield f"F{nd.to_gcode(self.feed_)}"

    def accumulate_parts():
        match self.space_:
            case MovementSpace.MACHINE:
                yield "G01"
                yield "G53"
                yield from accumulate_relorabs()
                yield from accumulate_probe()
                yield from accumulate_mcode()
            case MovementSpace.WORK:
                yield "G01"
                yield from accumulate_relorabs()
                yield from accumulate_probe()
                yield from accumulate_mcode()
            case MovementSpace.R9810:
                yield "G65 R9810"
                if self.relorabs_ & MovementRelOrAbs.RELATIVE:
                    err.compiler("Relative with 9810 move is illegal.")

                if self.probe_:
                    err.compiler("Probe with 9810 move is illegal.")

                if self.mcode_:
                    err.compiler("MCODE with 9810 move is illegal.")

        yield from accumulate_feed()

    def get_coords():
        values = coords.unpack(args, kwargs)
        for aname, value in zip(axis.low_names_v(), values):
            # skip non important coords
            if fter and aname not in fter:
                continue
            # skip non mentioned coords
            if value.is_none_constant:
                continue
            yield aname, value

    def accumulate_coords(cos):
        for aname, value in cos:
            yield f"{aname}{value.to_gcode(nd.NodeModifier.EMPTY)}"

    cos = list(get_coords())
    if not cos:
        return

    stat.code(
        accumulate_parts(),
        accumulate_coords(cos),
    )


@dataclasses.dataclass(eq=True, frozen=True)
class GotoWorker:
    user_defined = True
    want_bp_: bool
    space_: MovementSpace
    order_: MovementOrder
    relorabs_: MovementRelOrAbs
    feed_: float
    probe_: bool
    mcode_: str

    def to_symtab_entry(self, *_) -> str:
        return "".join(
            [
                str(self.feed_),
                " ",
                self.mcode_ + " " if self.mcode_ else "",
                self.space_.name.lower(),
                " ",
                self.order_.name.lower(),
                " ",
                "probe " if self.probe_ else "",
                "bp" if self.want_bp_ else "",
            ]
        )

    def update(self, key, value):
        xxx = {**self.__dict__, key: value}
        return GotoWorker(**xxx)

    @property
    def work(self):
        return self.update("space_", MovementSpace.WORK)

    @property
    def r9810(self):
        return self.update("space_", MovementSpace.R9810)

    @property
    def machine(self):
        return self.update("space_", MovementSpace.MACHINE)

    @property
    def z_then_xy(self):
        return self.update("order_", MovementOrder.Z_THEN_XY)

    @property
    def xy_then_z(self):
        return self.update("order_", MovementOrder.XY_THEN_Z)

    @property
    def probe(self):
        return self.update("probe_", True)

    @property
    def xyz(self):
        return self.update("order_", MovementOrder.XYZ)

    @property
    def relative(self):
        return self.update("relorabs_", MovementRelOrAbs.RELATIVE)

    @property
    def absolute(self):
        return self.update("relorabs_", MovementRelOrAbs.ABSOLUTE)

    def feed(self, feed):
        return self.update("feed_", feed)

    def mcode(self, m_code):
        return self.update("mcode_", str(m_code))

    def __call__(self, *args, **kwargs):
        match self.order_:
            case MovementOrder.XYZ:
                do_goto_worker(self, "", args, kwargs)
            case MovementOrder.Z_THEN_XY:
                do_goto_worker(self, "z", args, kwargs)
                do_goto_worker(self, "xy", args, kwargs)
            case MovementOrder.XY_THEN_Z:
                do_goto_worker(self, "xy", args, kwargs)
                do_goto_worker(self, "z", args, kwargs)


gbl.HasToSymTab.register(GotoWorker)
goto = GotoWorker(
    want_bp_=False,
    space_=MovementSpace.WORK,
    relorabs_=MovementRelOrAbs.ABSOLUTE,
    order_=MovementOrder.XYZ,
    feed_=0.0,
    probe_=False,
    mcode_="",
)
