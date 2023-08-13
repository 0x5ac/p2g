import p2g
from conftest import want


class Params:
    dir: p2g.Vec

    def __init__(self, src, dst):
        self.dir = src - dst


# TESTS BELOW
########################################
@want(
    "O00001 (test_prec1)                               ",
    "( here = Params[Const[1, 2], Var[x=3, y=10]])     ",
    "  #100= 3.                                        ",
    "  #101= 10.                                       ",
    "( goto.feed[10].machine.all[here.dir])            ",
    "  G90 G53 G01 G55 F10. x[1. - #100] y[2. - #101]  ",
    "  M30                                             ",
    "%                                                 ",
)
def test_prec1():
    here = Params(p2g.Const(1, 2), p2g.Var(x=3, y=10))

    p2g.goto.feed(10).machine.all(here.dir)
