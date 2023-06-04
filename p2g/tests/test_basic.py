from p2g import *
from p2g.haas import *

X = Fixed[3](addr=203)


@must_be_cc(
    "( ha )",
    '( h"a" )',
    "( X.y = 2 * -1                  )",
    "  #204= -2.",
)
def test_0():
    comment("ha")
    comment('h"a"')
    X.y = 2 * -1


@must_be_cc("( ho )")
def test_del0():
    comment("ho")
    aa = {1: 2, 3: 4}
    del aa[1]


@must_be()
def test_del1():
    aa = 3
    del aa


@must_be(
    "( X.x = X.y * 0                 )",
    "  #203= 0.                    ",
)
def test_m0():
    X.x = X.y * 0
