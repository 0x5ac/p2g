import p2g

from conftest import want
from p2g import haas


# TESTS BELOW
@want(
    "O00001 (test_load_tool)",
    "( load_tool[12]                 )",
    "  T12 M06",
    "  M30",
    "%",
)
def test_load_tool():
    p2g.load_tool(12)


@want(
    "O00001 (test_no_lookahead)",
    "( No lookahead                  )",
    "  M97 P123",
    "  M30",
    "",
    "( No lookahead )",
    "N123",
    "  G103 P1",
    "  G04 P1",
    "  G04 P1",
    "  G04 P1",
    "  G04 P1",
    "  M99",
    "%",
)
def test_no_lookahead():
    p2g.no_lookahead()


@want(
    "O00001 (test_optional)",
    "(     Var[123]                  )",
    "/   #100= 123.",
    "  M30",
    "%",
)
def test_optional():

    with p2g.Optional():
        p2g.Var(123)


@want(
    "O00001 (test_wcs)",
    "( with WCS[haas.G55]:           )",
    "  #100= #4014",
    "  G55",
    "(     goto.work.feed[123].z_first[1, 2, 3])",
    "  G90 G01 G55 F123. z3.",
    "  G90 G01 G55 F123. x1. y2.",
    "( Restore wcs                   )",
    "  G[# 100]",
    "  M30",
    "%",
)
def test_wcs():

    with p2g.WCS(haas.G55):
        p2g.goto.work.feed(123).z_first(1, 2, 3)
