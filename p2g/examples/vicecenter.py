import csearch
import defs

import p2g

from p2g.haas import *


# describe relationship between x&y and left,right,far,near
#


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
    "left": Dinfo("left", "right", 0, (-1, 0)),
    "right": Dinfo("right", "left", 0, (1, 0)),
    "far": Dinfo("far", "near", 1, (0, 1)),
    "near": Dinfo("near", "far", 1, (0, -1)),
}


@p2g.inline
def prod_surface(st, sch, di, output):
    p2g.comment(
        "",
        f"quickly move probe to find {di.name} edge",
    )

    addr = p2g.base_addr()
    start_search = p2g.Const[2](sch.amin.xy * di.dxdy / 2.0)
    stop_search = p2g.Const[2](sch.amax.xy * di.dxdy / 2.0)
    delta = sch.delta * di.dxdy

    its = p2g.Var(
        (abs(stop_search - start_search) / sch.delta)[di.cur_axis] + 1,
    )
    cursor = st.cursor

    cursor[di.cur_axis] = start_search[di.cur_axis]

    while its > 0:
        st.goto(cursor)
        st.fast_probe(z=sch.search_depth)
        if SKIP_POS.z < sch.search_depth + sch.iota:
            break
        cursor.xy += delta
        its -= 1
    else:
        st.alarm(f"search for {di.name} failed")

    p2g.comment(
        f"back off a bit to the {di.name}, then slowly probe ",
        f"{di.opposite}wards for precise measurement.",
    )
    cursor.xy += sch.backoff * di.dxdy
    st.goto(cursor.xy)
    st.slow_probe([0, 0])

    # sets part of tlc or brc
    output[di.cur_axis] = (SKIP_POS + PROBE_R * di.dxdy)[di.cur_axis]

    p2g.comment(
        "reposition above surface skim height,",
        f"just inside {di.name} edge",
    )

    st.goto.relative(sch.backoff.xy * di.dxdy)
    st.goto(z=sch.skim_distance)
    cursor.xy += -sch.indent.xy * di.dxdy
    st.goto(cursor)
    p2g.base_addr(addr)


@p2g.inline
def find_surface_before(st, sch):
    p2g.set_wcs(st.WCS)

    st.goto.machine(z=0)

    st.goto.machine.xy_then_z(sch.above)

    p2g.comment(f"find top z roughly set {st.WCS}.z.")

    st.WCS.xyz = MACHINE_POS.xyz
    # fast find move down to min search distance
    st.fast_probe(z=sch.amin.z)

    # make work offset z make rough top 0.
    st.WCS.z = MACHINE_POS.z
    st.pause("check g55")

    p2g.comment(
        "now work.z should be 0 at surface",
        "and work.xy roughly middle",
    )
    st.goto(z=sch.skim_distance)

    st.tlc = p2g.Var[2]()
    st.brc = p2g.Var[2]()

    st.cursor = p2g.Var[2](0, 0)
    prod_surface(st, sch, dinfo["left"], st.tlc)
    prod_surface(st, sch, dinfo["near"], st.brc)
    prod_surface(st, sch, dinfo["far"], st.tlc)

    # move back to centerline
    st.goto(0, 0)
    prod_surface(st, sch, dinfo["right"], st.brc)

    p2g.comment(
        " the 'error' between 0,0 and where we",
        " calculate the center to be gets",
        " added to cos and voila.",
    )

    st.error = p2g.Var[2]((st.tlc + st.brc) / 2.0)
    st.WCS.xy += st.error.xy
    st.goto(0, 0)

    p2g.comment(" final slow probe to find the surface z")
    st.slow_probe(z=sch.search_depth)
    st.WCS.z = SKIP_POS.z

    st.goto.machine(z=sch.above.z)
    st.alarm(" what changed")


@p2g.inline
def runit(st, sch):
    st.WCS = G55

    p2g.comment(
        "Find center of plate in vice,",
        f" result in {st.WCS}",
        *sch.comment,
    )

    st.setup_probing()

    find_surface_before(st, sch)


def vicecenter():
    p2g.symbol.Table.print = True
    st = defs.JobDefs()

    sch = csearch.SearchConstraint(
        # minimum size expected
        amin=p2g.Const(x=7.0, y=4.0, z=-5.0),
        # maximum size expected
        amax=p2g.Const(x=14.0, y=8.0, z=3.0),
        delta=p2g.Const(x=0.75, y=0.4),
        above=st.MACHINE_ABS_ABOVE_VICE + p2g.Const(x=0.0, z=0.0, y=-3.0),
    )
    runit(st, sch)
