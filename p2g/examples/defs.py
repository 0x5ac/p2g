import enum

import p2g as p2g

from p2g.haas import *


class ONumbers(enum.IntEnum):
    PROBE_VICE_CENTER = 100
    ALIGNC = enum.auto()
    ROTARY_PROBE_BORE = enum.auto()
    ABOVE_VICE = enum.auto()
    ABOVE_ROTARY = enum.auto()
    PROBE_CALIBRATE = enum.auto()


class Tool(enum.IntEnum):
    PROBE = 1
    KNOWN_LENGTH = 2


# pylint: disable=too-many-instance-attributes
class JobDefs(p2g.Symbols):
    def __init__(self):
        super().__init__()
        self.MACHINE_ABS_ABOVE_OTS = p2g.Const(x=-1.16, y=-7.5, z=-8.0)
        self.MACHINE_ABS_ABOVE_RING = p2g.Const(x=-16.46, y=-3.5, z=-22.7)
        self.MACHINE_ABS_ABOVE_ROTARY = p2g.Const(x=-12.5214, y=-12.9896, z=-7.0)
        self.MACHINE_ABS_ABOVE_SEARCH_ROTARY_LHS_5X8 = p2g.Const(
            x=-15.5, y=-17.50, z=-14.0
        )
        self.MACHINE_ABS_ABOVE_VICE = p2g.Const(x=-28.0, y=-10.0, z=-16.00)
        self.MACHINE_ABS_CLOSE_ABOVE_OTS = p2g.Const(x=-1.16, y=-7.5, z=-7.6)
        self.MACHINE_ABS_CLOSE_ABOVE_TOOL_TOUCH = p2g.Const(
            x=-1.16,
            y=-7.5,
            z=-7.6,
        )
        self.MACHINE_ABS_HOME2 = p2g.Const(x=-15.0, y=-15.0, z=-2.0)
        self.MACHINE_ABS_ROTARY_HOME = p2g.Const(x=-12, y=0.0, z=-3.0)
        self.MACHINE_ABS_Z0 = p2g.Const(z=0.0)

        self.MACHINE_ABS_ZMIN = p2g.Const(z=-22.0)
        self.PROBE_RING_DIAMETER = 0.7
        m1 = p2g.Const(x=0.0, y=0.0, z=-0.7)
        self.MACHINE_ABS_SEARCH_ROTARY_LHS_5X8 = (
            self.MACHINE_ABS_ABOVE_SEARCH_ROTARY_LHS_5X8 + m1
        )

        self.FAST_FEED = 650.0
        self.SLOW_PROBE_FEED = 10.0
        self.FAST_PROBE_FEED = 100.0

        probe = p2g.goto.probe.mcode(MUST_SKIP).work
        self.slow_probe = probe.feed(self.SLOW_PROBE_FEED)

        self.fast_probe = probe.feed(self.FAST_PROBE_FEED)
        self.goto = p2g.goto.work.feed(self.FAST_FEED)

        self.init_finished()

    def load_tool(self, tool):
        p2g.code(f"T{tool:02} M06")

    def setup_probing(self):
        self.load_tool(Tool.PROBE)

        p2g.code(PROBE_ON)
        p2g.code(NO_LOOKAHEAD)

    def message(self, txt: str, code: int = 101):
        p2g.message(MESSAGE[0], txt, code=code)

    def alarm(self, txt: str, code: int = 101):
        p2g.message(ALARM[0], txt, code=code)

    def ots_on(self):
        p2g.code(OTS_ON)

    def spindle_probe_on(self):
        p2g.code(SPINDLE_PROBE_ON)

    def ots_calibrate(self):
        p2g.code("G65 P9023 A20. K5. S0.5 D-2.")

    def spindle_probe_find_height(self):
        p2g.code("G65 P9023 A21. T1.")

    def spindle_probe_find_radius(self):
        p2g.code("G65 P9023 A10.0 D0.7")
