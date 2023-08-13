import enum

import p2g


class Tool(enum.IntEnum):
    PROBE = 1
    KNOWN_LENGTH = 2


# pylint: disable=too-many-instance-attributes
# all coords are  abs end of spindle probe.
# ots tool and probe are different lengths.

KNOWNLEN_DIFF = -0.25
KNOWNLEN_OFF = p2g.Const(0, 0, KNOWNLEN_DIFF)
MABS_ABOVE_OTS = p2g.Const(x=-1.167, y=-7.56, z=-7.54)
MABS_INSIDE_RING = p2g.Const(x=-16.42, y=-3.42, z=-22.6)
MABS_ABOVE_ROTARY = p2g.Const(x=-12.5214, y=-12.9896, z=-7.0)
MABS_ABOVE_SEARCH_ROTARY_LHS_5X8 = p2g.Const(x=-15.5, y=-17.50, z=-14.0)
MABS_ABOVE_VICE = p2g.Const(x=-27.5, y=-13.0, z=-17.5)

PROBE_RING_DIAMETER = 0.7
FAST_FEED = 600.0
SLOW_PROBE_FEED = 10.0
FAST_PROBE_FEED = 60.0

must_skip_probe = p2g.goto.probe.mcode(p2g.haas.MUST_SKIP)
may_skip_probe = p2g.goto.probe

_slow_rel_probe = must_skip_probe.delay(0).relative.feed(SLOW_PROBE_FEED).all
_fast_rel_probe = must_skip_probe.relative.relative.all.feed(FAST_PROBE_FEED)
_fast_work_probe = may_skip_probe.work.feed(FAST_PROBE_FEED).all
_slow_work_probe = may_skip_probe.work.feed(SLOW_PROBE_FEED).all


def slow_rel_probe(**cos):
    _slow_rel_probe(**cos)


#    p2g.no_lookahead()


def slow_work_probe(**cos):
    _slow_work_probe(**cos)


#    p2g.no_lookahead()


def fast_rel_probe(**cos):
    _fast_rel_probe(**cos)


#    p2g.no_lookahead()


def fast_work_probe(**cos):
    _fast_work_probe(**cos)


#    p2g.no_lookahead()


goto_work = p2g.goto.work.feed(FAST_FEED).all
goto_G53 = p2g.goto.machine.feed(FAST_FEED)

# goto_down  - safeish way to go down,
# move xy first and then z.
goto_down = p2g.goto.work.feed(FAST_FEED).z_last

# goto_up  - safeish way to go up.
# move z first and then xy.

goto_up = p2g.goto.work.feed(FAST_FEED).z_first


goto_rel = p2g.goto.relative.feed(FAST_FEED).all
goto_work_z_first = p2g.goto.work.feed(FAST_FEED).z_first
goto = p2g.goto.work.feed(FAST_FEED).all


def goto_home():
    goto_G53.z_first(0, 0, 0)


def goto_zhome():
    goto_G53.all(z=0)


def setup_probing():
    load_tool(Tool.PROBE)
    p2g.codenl(p2g.haas.PROBE_ON, comment_txt=p2g.stat.CommentGen.FROMSRC)
    p2g.codenl(p2g.haas.NO_LOOKAHEAD, comment_txt=p2g.stat.CommentGen.NONE)


def pause(txt: str):
    p2g.comment()
    p2g.sys.message(p2g.haas.MESSAGE[0], txt)
    p2g.comment()


def alarm(txt: str):
    p2g.sys.message(p2g.haas.ALARM[0], txt)


def ots_calibrate():
    p2g.codenl("G65 P9023 A20. K5. S0.5 D-2.", comment_txt=p2g.stat.CommentGen.FROMSRC)


def spindle_probe_find_height():
    p2g.codenl("G65 P9023 A21. T1.", comment_txt=p2g.stat.CommentGen.FROMSRC)


def spindle_probe_find_radius(diameter):
    p2g.codenl(f"G65 P9023 A10.0 D{diameter}", comment_txt=p2g.stat.CommentGen.FROMSRC)


def load_tool(tool):
    p2g.codenl(f"T{tool:02} M06", comment_txt=p2g.stat.CommentGen.FROMSRC)


class Probe:
    def __enter__(self):
        load_tool(Tool.PROBE)
        p2g.codenl(p2g.haas.SPINDLE_PROBE_ON, comment_txt="Probe on.")

    def __exit__(self, *_):
        p2g.codenl(p2g.haas.SPINDLE_PROBE_OFF, comment_txt="Probe off.")


class OTS:
    def __enter__(self):
        load_tool(Tool.KNOWN_LENGTH)
        p2g.codenl(p2g.haas.OTS_ON, comment_txt="OTS On.")

    def __exit__(self, *_):
        p2g.codenl(p2g.haas.OTS_OFF, comment_txt="OTS Off.")


def optional_pause(txt: str):
    with p2g.sys.Optional():
        p2g.comment()
        pause(txt)
        p2g.comment()
