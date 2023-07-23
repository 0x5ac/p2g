from typing import Optional

import p2g


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
        initial_search_depth=None,
        found_if_below=None,
    ):
        super().__init__()

        if initial_search_depth is None:
            initial_search_depth = p2g.Const(-1.0)

        if search_depth is None:
            search_depth = p2g.Const(-0.1)

        if found_if_below is None:
            found_if_below = search_depth * 0.8

        if backoff is None:
            backoff = p2g.Const(x=0.1, y=0.1, z=0.1)

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
        self.initial_search_depth = initial_search_depth
        self.found_if_below = found_if_below
        self.edge_search_depth = -0.1

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
