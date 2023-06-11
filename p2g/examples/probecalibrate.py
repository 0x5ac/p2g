#! /usr/bin/env python
import sys

import defs

from p2g import *


symbol.Table.print = 1


def probecalibrate():
    symbol.Table.print = 1
    st = defs.JobDefs()

    comment(
        "Calibrate from known length tool,",
        "first macke sure OTS working, move tool",
        "to above setter, and runs calibrate",
        "macro.",
    )

    st.load_tool(defs.Tool.KNOWN_LENGTH)
    st.ots_on()
    st.goto.machine(z=0)
    st.pause("touch OTS, must beep")

    st.goto.machine.xy_then_z(st.MACHINE_ABS_ABOVE_OTS)
    st.ots_calibrate()

    comment(
        "Calibrate the spindle probe.",
        "load spindle probe, makes sure the",
        "battery isn't flat, checks it over the ",
        "tool setter, and then in the fixed ring",
    )

    st.load_tool(defs.Tool.PROBE)
    st.spindle_probe_on()

    st.pause("touch probe, must beep")

    comment("test spindle probe with OTS")
    st.goto.machine(z=0)

    st.goto.machine.xy_then_z(st.MACHINE_ABS_ABOVE_OTS_FOR_PROBE)

    st.spindle_probe_find_height()

    comment("test spindle probe with ring.")
    st.goto.machine(z=0)
    st.goto.machine.xy_then_z(st.MACHINE_ABS_ABOVE_RING)
    st.spindle_probe_find_radius()
    st.goto.machine(z=0)
