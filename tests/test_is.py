import p2g
from conftest import want


class X:
    def __init__(self, y=None):
        if y is None:
            self.p = 2
        else:
            self.p = y


# TESTS BELOW
########################################
@want(
    "O00001 (test_with_const)                          ",
    "( Var[9 == 9]                   )                 ",
    "  #100= 1.                                        ",
    "( C )                                             ",
    "  M30                                             ",
    "%                                                 ",
)
def test_with_const():
    p2g.Var(9 == 9)
    p2g.com("C")


########################################
@want(
    "O00001 (test_with_none)                           ",
    "( Var[x.p]                      )                 ",
    "  #100= 2.                                        ",
    "( A )                                             ",
    "  M30                                             ",
    "%                                                 ",
)
def test_with_none():
    x = X()
    p2g.Var(x.p)
    p2g.com("A")


########################################
@want(
    "O00001 (test_with_something)                      ",
    "( Var[x.p]                      )                 ",
    "  #100= 2.                                        ",
    "( B )                                             ",
    "  M30                                             ",
    "%                                                 ",
)
def test_with_something():
    x = X(7)
    p2g.Var(x.p)
    p2g.com("B")
