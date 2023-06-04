#! /usr/bin/env python
import sys

import defs

import p2g as pg


def probecalibrate():
    st = defs.JobDefs()

    pg.comment(
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

    pg.comment("Calibrate spindle probe.")

    st.load_tool(defs.Tool.PROBE)
    st.spindle_probe_on()

    st.message("touch probe, must beep")

    pg.comment("test spindle probe with OTS.")
    st.goto.machine(z=0)
    st.goto.machine.xy_then_z(st.MACHINE_ABS_ABOVE_OTS)

    st.spindle_probe_find_height()

    pg.comment("test spindle probe with ring.")
    st.goto.machine(z=0)
    st.goto.machine.xy_then_z(st.MACHINE_ABS_ABOVE_RING)
    st.spindle_probe_find_radius()
    st.goto.machine(z=0)
