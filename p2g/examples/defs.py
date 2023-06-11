import enum

from p2g import *
from p2g.haas import *


# class ONumbers(enum.IntEnum):
#     PROBE_VICE_CENTER = 100
#     ALIGNC = enum.auto()
#     ROTARY_PROBE_BORE = enum.auto()
#     ABOVE_VICE = enum.auto()
#     ABOVE_ROTARY = enum.auto()
#     PROBE_CALIBRATE = enum.auto()


class Tool(enum.IntEnum):
    PROBE = 1
    KNOWN_LENGTH = 2


# pylint: disable=too-many-instance-attributes
class JobDefs(Table):
    def __init__(self):
        super().__init__()
        self.MACHINE_ABS_ABOVE_OTS = Const(x=-1.16, y=-7.5, z=-7.2)
        # difference in length between fixed length probe and spindle probe.
        self.MACHINE_ABS_ABOVE_OTS_FOR_PROBE = self.MACHINE_ABS_ABOVE_OTS + (
            0,
            0,
            1,
        )
        self.MACHINE_ABS_ABOVE_RING = Const(x=-16.46, y=-3.5, z=-22.7)
        self.MACHINE_ABS_ABOVE_ROTARY = Const(x=-12.5214, y=-12.9896, z=-7.0)
        self.MACHINE_ABS_ABOVE_SEARCH_ROTARY_LHS_5X8 = Const(x=-15.5, y=-17.50, z=-14.0)
        self.MACHINE_ABS_ABOVE_VICE = Const(x=-28.0, y=-10.0, z=-16.00)

        self.MACHINE_ABS_CLOSE_ABOVE_TOOL_TOUCH = Const(
            x=-1.16,
            y=-7.5,
            z=-7.6,
        )
        self.MACHINE_ABS_HOME2 = Const(x=-15.0, y=-15.0, z=-2.0)
        self.MACHINE_ABS_ROTARY_HOME = Const(x=-12, y=0.0, z=-3.0)
        self.MACHINE_ABS_Z0 = Const(z=0.0)

        self.MACHINE_ABS_ZMIN = Const(z=-22.0)
        self.PROBE_RING_DIAMETER = 0.7
        m1 = Const(x=0.0, y=0.0, z=-0.7)
        self.MACHINE_ABS_SEARCH_ROTARY_LHS_5X8 = (
            self.MACHINE_ABS_ABOVE_SEARCH_ROTARY_LHS_5X8 + m1
        )

        self.FAST_FEED = 65.0
        self.SLOW_PROBE_FEED = 10.0
        self.FAST_PROBE_FEED = 10.0

        probe = goto.probe.mcode(MUST_SKIP).work
        self.slow_probe = probe.feed(self.SLOW_PROBE_FEED)

        self.fast_probe = probe.feed(self.FAST_PROBE_FEED)
        self.goto = goto.work.feed(self.FAST_FEED)

    def load_tool(self, tool):
        code(f"T{tool:02} M06")

    def setup_probing(self):
        self.load_tool(Tool.PROBE)

        code(PROBE_ON)
        code(NO_LOOKAHEAD)

    def pause(self, txt: str):
        comment()
        message(MESSAGE, txt)
        comment()

    def alarm(self, txt: str):
        comment()
        message(ALARM, txt)
        comment()

    def ots_on(self):
        code(OTS_ON)

    def spindle_probe_on(self):
        code(SPINDLE_PROBE_ON)

    def ots_calibrate(self):
        code("G65 P9023 A20. K5. S0.5 D-2.")

    def spindle_probe_find_height(self):
        code("G65 P9023 A21. T1.")

    def spindle_probe_find_radius(self):
        code("G65 P9023 A10.0 D0.7")
