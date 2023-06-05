#! /usr/bin/env python
import sys

import defs

from p2g import *


def probecalibrate():
    st = defs.JobDefs()

    comment(
        "Start with fixed height probe,",
        "make sure probe stickout <2.25in",
    )
    st.insert_symbol_table()
    st.load_tool(defs.Tool.KNOWN_LENGTH)
    st.ots_on()
    st.goto(z=0)
    st.message("touch OTS, must beep")
    st.goto.machine.xy_then_z(st.MACHINE_ABS_ABOVE_OTS)

    st.message("Make sure tool position looks safe.")
    st.goto.machine(z=st.MACHINE_ABS_CLOSE_ABOVE_OTS.z)
    st.ots_calibrate()

    comment("Calibrate spindle probe.")

    st.load_tool(defs.Tool.PROBE)
    st.spindle_probe_on()

    st.message("touch probe, must beep")

    comment("test spindle probe with OTS.")
    st.goto.machine(z=0)
    st.goto.machine.xy_then_z(st.MACHINE_ABS_ABOVE_OTS)

    st.spindle_probe_find_height()

    comment("test spindle probe with ring.")
    st.goto.machine(z=0)
    st.goto.machine.xy_then_z(st.MACHINE_ABS_ABOVE_RING)
    st.spindle_probe_find_radius()
    st.goto.machine(z=0)
