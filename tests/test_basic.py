import p2g

from conftest import want


X = p2g.Fixed[3](addr=203)

# TESTS BELOW
########################################
@want(
    "O00001 (test_0)                                   ",
    "                                                  ",
    "( ha )                                            ",
    "                                                  ",
    '( h"a" )                                          ',
    "( X.y = 2 * -1                  )                 ",
    "  #204= -2.                                       ",
    "  M30                                             ",
    "%                                                 ",
)
def test_0():
    p2g.comment("ha")
    p2g.comment('h"a"')
    X.y = 2 * -1


########################################
@want(
    "O00001 (test_del0)                                ",
    "                                                  ",
    "( ho )                                            ",
    "  M30                                             ",
    "%                                                 ",
)
def test_del0():
    p2g.comment("ho")
    aa = {1: 2, 3: 4}
    del aa[1]


########################################
@want(
    "O00001 (test_del1)                                ",
    "  M30                                             ",
    "%                                                 ",
)
def test_del1():
    aa = 3
    del aa


########################################
@want(
    "O00001 (test_m0)                                  ",
    "( X.x = X.y * 0                 )                 ",
    "  #203= 0.                                        ",
    "  M30                                             ",
    "%                                                 ",
)
def test_m0():
    X.x = X.y * 0
