import p2g

from conftest import want


# TESTS BELOW
########################################
@want(
    "O00001 (test_ok)                                  ",
    "( zz[0] = 3                     )                 ",
    "  #100= 3.                                        ",
    "  M30                                             ",
    "%                                                 ",
)
def test_ok():
    p2g.Table()

    zz = p2g.Var[200]()
    zz[0] = 3


########################################
@want(
    "O00001 (test_ok2)                                 ",
    "( Fixed[2, addr=100]            )                 ",
    "  #100= 2.                                        ",
    "  M30                                             ",
    "%                                                 ",
)
def test_ok2():
    p2g.Fixed[200](addr=123)
    p2g.Fixed(2, addr=100)
