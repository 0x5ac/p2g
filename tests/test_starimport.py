from conftest import want
from p2g import *  # noqa: F403


# TESTS BELOW
@want(
    "O00001 (test_simplify1_fail)",
    "( Var[y[0] + -1 * 1.5]  # noqa: F405)",
    "  #100= #17 - 1.5",
    "  M30",
    "%",
)
def test_simplify1_fail():
    y = Fixed[1](addr=17)  # noqa: F405
    Var(y[0] + -1 * 1.5)  # noqa: F405
