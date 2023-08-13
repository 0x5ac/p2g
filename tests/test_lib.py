import p2g

from conftest import want


# TESTS BELOW
########################################
@want(
    "O00001 (test_load_tool)                           ",
    "( sys.load_tool[12]             )                 ",
    "  T12 M06                                         ",
    "  M30                                             ",
    "%                                                 ",
)
def test_load_tool():
    p2g.sys.load_tool(12)


########################################
@want(
    "O00001 (test_no_lookahead)                        ",
    "( sys.Lookahead[False]          )                 ",
    "  M97 P123                                        ",
    "  M30                                             ",
    "N123                                              ",
    "  G103 P1                                         ",
    "  G04 P1                                          ",
    "  G04 P1                                          ",
    "  G04 P1                                          ",
    "  G04 P1                                          ",
    "  M99                                             ",
    "%                                                 ",
)
def test_no_lookahead():
    p2g.sys.Lookahead(False)


########################################
@want(
    "O00001 (test_optional)                            ",
    "(     Var[123]                  )                 ",
    "/  #100= 123.                                     ",
    "  M30                                             ",
    "%                                                 ",
)
def test_optional():
    with p2g.sys.Optional():
        p2g.Var(123)


########################################
@want(
    "O00001 (test_wcs)                                 ",
    "( with sys.WCS[haas.G55]:       )                 ",
    "  #100= #4014                                     ",
    "  G55                                             ",
    "(     goto.work.feed[123].z_first[1, 2, 3])       ",
    "  G90 G01 G55 F123. z3.                           ",
    "  G90 G01 G55 F123. x1. y2.                       ",
    "( Restore wcs                   )                 ",
    "  G[# 100]                                        ",
    "  M30                                             ",
    "%                                                 ",
)
def test_wcs():

    with p2g.sys.WCS(p2g.haas.G55):
        p2g.goto.work.feed(123).z_first(1, 2, 3)
