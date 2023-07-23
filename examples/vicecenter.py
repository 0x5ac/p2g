import csearch
import defs
import p2g
from p2g import haas


sch = csearch.SearchConstraint(
    # minimum size expected
    amin=p2g.Const(x=8.0, y=4.0, z=1.0),
    # maximum size expected
    amax=p2g.Const(x=16.0, y=9.0, z=3.0),
    delta=p2g.Const(x=1.0, y=1.0),
    above=defs.MABS_ABOVE_VICE,
)


def no_lookahead():
    p2g.no_lookahead()


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


def find_top(wcs):
    p2g.comment("find top z roughly.")

    defs.goto(z=0)

    p2g.comment("just above workpiece surface.")
    defs.goto_down(sch.above)

    # fast find move down to min search distance
    defs.fast_work_probe(z=sch.above.z + sch.initial_search_depth)

    p2g.com("make wcs become ~0,0,0 at tdc")
    wcs.xyz = +haas.SKIP_POS

    defs.goto(z=sch.skim)
    p2g.comment(
        "now work.xyz should be 0, with z at skim",
        "distance, physically roughly tdc",
    )


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

    defs.optional_pause(f"top of {di.name}")
    # move the interesting dimension to at least the minimum
    # distance for an edge.
    defs.goto_up(sch.amin.xy * di.dxdy * 0.5, z=sch.skim)
    while its > 0:
        defs.goto_rel(delta.xy)
        defs.fast_work_probe.all(z=sch.search_depth)
        if haas.SKIP_POS.z < sch.found_if_below:
            break
        defs.goto(z=sch.skim)
        its -= 1
    else:
        defs.alarm(f"search for {di.name} failed")


# backoff from the direction being inspected
# for a slow approach.
def backoff_and_slow_probe(edge_name, error):
    di = dinfo[edge_name]
    p2g.comment(
        f"Accurately find {di.name} edge: ",
        f" Back off a bit {di.name}wards.",
        " Move to search height.",
        f" Slowly probe towards the {di.opposite}",
        " edge.",
    )
    defs.goto(z=sch.search_depth)
    defs.goto_rel(sch.backoff.xy * di.dxdy)
    defs.slow_rel_probe(-sch.indent.xy * di.dxdy)
    # no need to adjust by probe_r, since errors will
    # cancel out.
    error[di.cur_axis] += haas.SKIP_POS[di.cur_axis]


def move_above_and_inwards(edge_name):
    di = dinfo[edge_name]
    p2g.comment(
        "Above surface and in:",
        f" Back off {edge_name} edge, up to skim distance.",
        " Move towards center.",
    )

    defs.goto_rel(sch.backoff.xy * di.dxdy)
    defs.goto(z=sch.skim)
    defs.goto_rel(-sch.indent.xy * di.dxdy)


def find_edge(edge_name, error):

    with p2g.BSS():
        fast_find(edge_name)
        backoff_and_slow_probe(edge_name, error)
        move_above_and_inwards(edge_name)


def find_edges(error):
    # enter at roughly 0,0,0

    find_edge("left", error)
    find_edge("near", error)
    find_edge("far", error)
    defs.goto(0, 0)
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
    defs.goto(0, 0)

    p2g.comment(" final slow probe to find the surface z")
    defs.slow_rel_probe(z=sch.search_depth)
    wcs.z += haas.SKIP_POS.z
    defs.goto(z=1)
    defs.pause(" what changed")


def vicecenter():
    p2g.comment(
        "Find center of plate in vice,",
        *sch.comment,
    )
    p2g.symbol.Table.print = True
    with (
        p2g.WCS(haas.G55) as wcs,
        defs.Probe(),
    ):
        # start with g55 same as machine coords.
        haas.G55.xyz = (0, 0, 0)
        error = p2g.Var[2](0, 0)

        find_top(wcs)
        find_edges(error)
        calc_center(wcs, error)

        find_top(wcs)
        find_edges(error)
        calc_center(wcs, error)
