import dataclasses
import enum

from p2g import axis
from p2g import coords
from p2g import err
from p2g import nd
from p2g import stat


# fast and slow and neither look up params.
# can be changed by using explicit feed.
# kwargs could contain x,y,z,feed ec
# as could extras


class MovementSpace(enum.IntEnum):
    WORK = enum.auto()
    MACHINE = enum.auto()
    RELATIVE = enum.auto()


class MovementOrder(enum.IntEnum):
    XYZ = enum.auto()
    XY_THEN_Z = enum.auto()
    Z_THEN_XY = enum.auto()


def do_goto_worker(self, fter, args, kwargs):
    # split out arguments we understand from
    # ones for coordinates.

    values = coords.unpack(args, kwargs)

    res = ["G01"]

    match self.space_:
        case MovementSpace.MACHINE:
            res.append("G90")
            res.append("G53")
        case MovementSpace.RELATIVE:
            res.append("G91")
        case MovementSpace.WORK:
            res.append("G90")

    if self.probe_:
        res.append("G31")
    if self.mcode_:
        res.append(self.mcode_)

    if self.feed_ == 0.0:
        err.compiler("Need feed rate.")

    res.append(f"F{nd.to_gcode(self.feed_)}")

    for aname, value in zip(axis.low_names_v(), values):
        if fter and aname not in fter:
            continue

        if value.is_none_constant:
            continue
        res.append(f"{aname}{value.to_gcode(nd.NodeModifier.EMPTY)}")
    rtxt = " ".join(res)

    stat.code(rtxt)


@dataclasses.dataclass(eq=True, frozen=True)
class GotoWorker:
    user_defined = True
    want_bp_: bool
    space_: MovementSpace
    feed_: float
    order_: MovementOrder
    probe_: bool
    mcode_: str

    def __eq__(self, x):
        breakpoint()

    def __lt__(self, x):
        breakpoint()

    def __hash__(self):
        v = object.__hash__(self)
        breakpoint()
        return v

    def to_symtab_entry(self, *_):
        return " ".join(
            [
                "probe" if self.probe_ else "",
                self.mcode_ if self.mcode_ else "",
                self.space_.name.lower(),
                self.order_.name.lower(),
                "bp" if self.want_bp_ else "",
                str(self.feed_),
            ]
        )

    def update(self, key, value):
        xxx = {**self.__dict__, key: value}
        breakpoint()
        return GotoWorker(**xxx)

    @property
    def work(self):
        return self.update("space_", MovementSpace.WORK)

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
        return self.update("space_", MovementSpace.RELATIVE)

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


goto = GotoWorker(
    want_bp_=False,
    space_=MovementSpace.WORK,
    feed_=0.0,
    order_=MovementOrder.XYZ,
    probe_=False,
    mcode_="",
)
