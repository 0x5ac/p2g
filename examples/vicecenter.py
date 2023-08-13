from typing import Optional
import p2g


import usrlib as usr
from p2g import sys
from p2g.sys import print


class SearchConstraint:
    # position roughly center above start of search.
    above: p2g.Vec
    # min size of thing to look for.

    amin: p2g.Vec
    # max size to search in one dimension for the thing
    # to probe.  p2g.RVALnstains max size of things measured.
    amax: p2g.Vec

    # when measuring z, how far to
    # move from an xy edge inwards to work it out.
    indent: p2g.Vec

    # steps between probes

    delta: p2g.Vec
    # safe distance above probed z surface to move
    skim: p2g.Vec

    # how far to backoff before probing slowly
    backoff: p2g.Vec

    # how far to look down for a surface once we've
    # already located the rough z0
    search_depth: p2g.Vec
    # how far to look down and not found is a not there
    #
    found_if_below: p2g.Vec

    def __init__(
        self,
        amin: p2g.Vec,
        amax: p2g.Vec,
        above: p2g.Vec,
        delta: p2g.Vec,
        skim=None,
        indent: Optional[p2g.Vec] = None,
        backoff: Optional[p2g.Vec] = None,
        search_depth=None,
        zslack=None,
        found_if_below=None,
    ):

        if zslack is None:
            zslack = p2g.Const(-1.0)

        if search_depth is None:
            search_depth = p2g.Const(-0.1)

        if found_if_below is None:
            found_if_below = search_depth * 0.8

        if backoff is None:
            backoff = p2g.Const(x=0.05, y=0.05, z=0.05)

        if indent is None:
            indent = round(amax * 0.1, 1)

        if skim is None:
            skim = p2g.Const(0.15)

        self.delta = delta

        self.amin = amin
        self.indent = indent
        self.amax = amax
        self.above = above
        self.skim = skim
        self.backoff = backoff
        self.search_depth = search_depth
        self.zslack = zslack
        self.found_if_below = found_if_below
        self.edge_search_depth = -0.1

    def comment(self):
        return [
            "Search Constraints:",
            "start:",
            f"  {self.above}",
            "boundary:",
            f"  x= (-{(self.amax[0] * 0.5)}..-{(self.amin[0] * 0.5)})"
            f"..({(self.amin[0] * 0.5)}..{(self.amax[0] * 0.5)})",
            f"  y= (-{(self.amax[1] * 0.5)}..-{(self.amin[1] * 0.5)})"
            f"..({(self.amin[1] * 0.5)}..{(self.amax[1] * 0.5)})",
            f"  z= ({(-self.amax[2])}..{(-self.amin[2])})",
            "indent:",
            f"  {self.indent}",
            "delta:",
            f"  {self.delta}",
        ]


sch = SearchConstraint(
    # minimum size expected
    amin=p2g.Const(x=8.0, y=4.0, z=1.0),
    # maximum size expected
    amax=p2g.Const(x=16.0, y=9.0, z=3.2),
    delta=p2g.Const(x=1.0, y=1.0),
    above=usr.MABS_ABOVE_VICE,
)


# describe relationship between x&y and left,right,far,near
class Dinfo:
    name: str
    opposite: str
    cur_axis: int
    dxdy: tuple[float, float]

    def __init__(self, name, opposite, cur_axis, dxdy):
        self.name = name
        self.opposite = opposite
        self.cur_axis = cur_axis
        self.dxdy = dxdy


dinfo = {
    "left": Dinfo("left", "right", 0, (-1, None)),
    "right": Dinfo("right", "left", 0, (1, None)),
    "far": Dinfo("far", "near", 1, (None, 1)),
    "near": Dinfo("near", "far", 1, (None, -1)),
}


def show3(v):
    return f"{v:###.####?, }"


def find_top(wcs):
    p2g.comment("find top z roughly.")

    usr.goto(z=0)

    p2g.comment("just above workpiece surface.")
    usr.goto_down(sch.above)

    # fast find move down to min search distance
    usr.fast_work_probe(z=sch.above.z + sch.zslack)

    p2g.com("make wcs become ~0,0,0 at tdc")
    wcs.xyz = +p2g.haas.SKIP_POS

    usr.goto(z=sch.skim)
    p2g.comment(
        "now work.xyz should be 0, with z at skim",
        "distance, physically roughly tdc",
    )
    print("first estimate:")
    print(f"wcs now       {wcs[:2]:###.####?, }")


#    {wcs.x:5.2f}{wcs.y:5.2f}{wcs.z:5.2f}")


# finds the edge asked for by st and sch using
# edge_name as direction.
# asssumes probe is skimming over
# start pos, moves in direction. finds edge.
# stops there.


def fast_find(edge_name):
    di = dinfo[edge_name]
    start_search = p2g.Const[2](sch.amin.xy * di.dxdy / 2)
    stop_search = p2g.Const[2](sch.amax.xy * di.dxdy / 2)
    delta = sch.delta * di.dxdy

    # work out how many iterations to get from
    # start position to end position.

    gap = (stop_search - start_search)[di.cur_axis]
    number_bumps = gap / delta[di.cur_axis]

    its = p2g.Var(abs(number_bumps) + 1)

    p2g.comment(
        f"Fast find {di.name} edge:",
        " Starting from min possible dimension,",
        f" move probe {di.name}wards by",
        " calculated delta. If surface not found,",
        " then done.",
    )

    usr.optional_pause(f"top of {di.name}")
    # move the interesting dimension to at least the minimum
    # distance for an edge.

    usr.goto_up(sch.amin.xy * di.dxdy * 0.5, z=sch.skim)

    while its > 0:
        usr.goto_rel(delta.xy)
        usr.fast_work_probe(z=sch.search_depth)
        if p2g.haas.SKIP_POS.z < sch.found_if_below:
            break
        usr.goto(z=sch.skim)
        its -= 1
    else:
        usr.alarm(f"search for {di.name} failed")


# backoff from the direction being inspected
# then probe fast towards the edge, backoff and
# then probe slowly.


def backoff_and_fast_then_slow_probe(edge_name, error):
    di = dinfo[edge_name]
    p2g.comment(
        f"Accurately find {di.name} edge: ",
        f" Back off a bit {di.name}wards.",
        " Move to search height.",
        f" Slowly probe towards the {di.opposite}",
        " edge.",
    )
    # away from edge.
    usr.goto_rel(sch.backoff.xy * di.dxdy)
    # back to nominal search for edge height.
    usr.goto(z=sch.search_depth)
    # fast towards edge
    usr.fast_rel_probe(xy=-sch.indent.xy * di.dxdy)
    # backoff a little
    usr.goto_rel(sch.backoff.xy * di.dxdy)
    # and slowly find edge.
    usr.slow_rel_probe(xy=-sch.indent.xy * di.dxdy)

    # no need to adjust by probe_r, since errors will
    # cancel out.
    error[di.cur_axis] += p2g.haas.SKIP_POS[di.cur_axis]
    print(f"at {edge_name.ljust(5)} error {error:###.####?, }")


def move_above_and_inwards(edge_name):
    di = dinfo[edge_name]
    p2g.comment(
        "Above surface and in:",
        f" Back off {edge_name} edge, up to skim distance.",
        " Move towards center.",
    )

    usr.goto_rel(sch.backoff.xy * di.dxdy)
    usr.goto(z=sch.skim)
    usr.goto_rel(-sch.indent.xy * di.dxdy)


def find_edge(edge_name, error):

    with sys.BSS():
        fast_find(edge_name)
        backoff_and_fast_then_slow_probe(edge_name, error)
        move_above_and_inwards(edge_name)


def find_edges(error):
    # enter at roughly 0,0,0

    find_edge("left", error)
    find_edge("near", error)
    find_edge("far", error)
    usr.goto(0, 0)
    find_edge("right", error)


def calc_center(wcs, error):
    p2g.comment(
        "The x coordinates of the left and right",
        "edge have been summed and put into",
        "error[0]. That value is double the error",
        "of the first guess, since every bit of",
        "error shifts the apparent locations of",
        "the left and right side (if the",
        "workpiece was exactly placed under the",
        "first approximation, the left and right",
        "coordinats would have been equal and",
        "opposite, so the sum would be zero. The",
        "same is true for error[1], for far and",
        "near.",
    )

    wcs.xy += error.xy / 2.0
    usr.goto(0, 0)
    p2g.comment(" final slow probe to find the surface z")
    usr.slow_work_probe(z=sch.search_depth)
    wcs.z += p2g.haas.SKIP_POS.z
    print(f"wcs done      {wcs[:3]:###.####?, }")
    usr.goto(z=1)


def vicecenter():
    p2g.Control.emacsclient = True
    p2g.Control.symbol_table = True
    p2g.comment(
        "Find center of plate in vice,",
        *sch.comment(),
    )

    with (
        sys.WCS(p2g.haas.G55) as wcs,
        usr.Probe(),
        p2g.sys.Lookahead(False),
    ):
        # start with g55 same as machine coords.
        p2g.haas.G55.xyz = (0, 0, 0)
        error = p2g.Var[2](0, 0)

        find_top(wcs)
        find_edges(error)
        calc_center(wcs, error)
