#! /usr/bin/env python

import p2g
import usrlib as defs


def probecalibrate():

    p2g.comment(
        "Start with fixed height probe,",
        "make sure probe stickout <2.25in",
    )

    p2g.Control.symbol_table = True

    defs.goto_home()

    with defs.OTS():
        defs.pause("touch OTS, must beep")
        defs.goto_down(defs.MABS_ABOVE_OTS + defs.KNOWNLEN_OFF)
        defs.ots_calibrate()

    with defs.Probe():
        p2g.comment("Calibrate spindle probe.")
        defs.pause("touch probe, must beep")

        defs.goto_home()
        defs.goto_down(defs.MABS_ABOVE_OTS)
        defs.spindle_probe_find_height()

        p2g.comment("test spindle probe with ring.")
        defs.goto_home()
        defs.goto_down(defs.MABS_INSIDE_RING)
        defs.spindle_probe_find_radius(defs.PROBE_RING_DIAMETER)
        defs.goto_home()
