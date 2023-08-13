import p2g

from conftest import want


# TESTS BELOW
########################################
@want(
    "O00001 (test_ifelse)                              ",
    "( v[0] = v[1] if v[2] else v[3] )                 ",
    "  #100= #101 * [#102 NE 0.] + #103 * [#102 EQ 0.] ",
    "  M30                                             ",
    "%                                                 ",
)
def test_ifelse():
    v = p2g.Fixed[10](addr=100)

    v[0] = v[1] if v[2] else v[3]


########################################
@want(
    "O00001 (test_rsub)                                ",
    "( v[0] = 1.0 - 2.0              )                 ",
    "  #100= -1.                                       ",
    "  M30                                             ",
    "%                                                 ",
)
def test_rsub():
    v = p2g.Fixed[10](addr=100)

    v[0] = 1.0 - 2.0


########################################
@want(
    "O00001 (test_rsub1)                               ",
    "( v[0] = j - v[1]               )                 ",
    "  #100= 1. - #101                                 ",
    "  M30                                             ",
    "%                                                 ",
)
def test_rsub1():
    v = p2g.Fixed[10](addr=100)
    j = 1
    v[0] = j - v[1]


########################################
@want(
    "O00001 (test_rsub2)                               ",
    "( v[0] = 1.0 - v[2]             )                 ",
    "  #100= 1. - #102                                 ",
    "  M30                                             ",
    "%                                                 ",
)
def test_rsub2():
    v = p2g.Fixed[10](addr=100)

    v[0] = 1.0 - v[2]
