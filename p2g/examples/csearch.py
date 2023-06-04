from typing import Optional

import p2g as pg


class SearchConstraint:
    # position roughly center above start of search.
    above: pg.Vec
    # min size of thing to look for.

    amin: pg.Vec
    # max size to search in one dimension for the thing
    # to probe.  pg.RVALnstains max size of things measured.
    amax: pg.Vec

    # when measuring z, how far to
    # move from an xy edge inwards to work it out.
    indent: pg.Vec

    # steps between probes

    delta: pg.Vec
    # safe distance above probed z surface to move
    skim_distance: pg.Vec

    # how far to backoff before probing slowly
    backoff: pg.Vec

    # how far to look down for a surface once we've
    # already located the rough z0
    search_depth: pg.Vec
    # how far to look down and not found is a not there
    #
    found_if_below: pg.Vec

    # to work out when there's a probe hit,
    # say probe from z down to 0,   then any stop < iota
    # is taken as a miss.
    iota: pg.Vec

    def __init__(
        self,
        amin: pg.Vec,
        amax: pg.Vec,
        above: pg.Vec,
        delta: pg.Vec,
        skim_distance=None,
        indent: Optional[pg.Vec] = None,
        backoff: Optional[pg.Vec] = None,
        search_depth=None,
        found_if_below=None,
        iota=None,
    ):
        super().__init__()

        if search_depth is None:
            search_depth = pg.Const(-0.1)

        if found_if_below is None:
            found_if_below = search_depth * 0.5

        if backoff is None:
            backoff = pg.Const(x=0.1, y=0.1, z=0.1)

        if indent is None:
            indent = round(amax * 0.1, 1)

        if skim_distance is None:
            skim_distance = pg.Const(0.3)

        if iota is None:
            iota = pg.Const(x=0.025, y=0.025, z=0.025)

        self.iota = iota
        self.delta = delta

        self.amin = amin
        self.indent = indent
        self.amax = amax

        self.above = above
        self.skim_distance = skim_distance
        self.backoff = backoff
        self.search_depth = search_depth
        self.found_if_below = found_if_below

    @property
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
