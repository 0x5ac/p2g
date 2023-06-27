import p2g

from p2g.haas import *
from p2g.ptest import must_be


@must_be(
    "( xyz = Var[LAST_TARGET_POS]    )",
    "  #100= #5001",
    "  #101= #5002",
    "  #102= #5003",
    "( xyz += 9                      )",
    "  #100= #100 + 9.",
    "  #101= #101 + 9.",
    "  #102= #102 + 9.",
)
def test_3axis():
    xyz = p2g.Var(LAST_TARGET_POS)
    xyz += 9


@must_be(
    "Bad axis letter in 'xyzabc'.",
    "p2g/tests/test_axes.py:8:4:7:     xyz.xyzabc = 32",
    "                                  ^^^",
)
def test_3axis1():
    xyz = p2g.Var(LAST_TARGET_POS)
    xyz.xyzabc = 32


@must_be(
    "( xyz = Var[LAST_TARGET_POS]    )",
    "  #100= #5001",
    "  #101= #5002",
    "  #102= #5003",
    "  #103= #5004",
    "  #104= #5005",
    "  #105= #5006",
    "( xyz.xyzabc = 32               )",
    "  #100= 32.",
    "  #101= 32.",
    "  #102= 32.",
    "  #103= 32.",
    "  #104= 32.",
    "  #105= 32.",
)
def test_6axis1():
    p2g.axis.NAMES = "xyzabc"
    xyz = p2g.Var(LAST_TARGET_POS)
    xyz.xyzabc = 32


@must_be(
    "( thing = Var[LAST_TARGET_POS]  )",
    "  #100= #5001",
    "  #101= #5002",
    "  #102= #5003",
    "  #103= #5004",
    "  #104= #5005",
    "( thing.xyzac = [1, 2, 3, 4, 5] )",
    "  #102= 1.",
    "  #103= 2.",
    "  #104= 3.",
    "  #100= 4.",
    "  #101= 5.",
)
def test_5axis():
    p2g.axis.NAMES = "acxyz"
    thing = p2g.Var(LAST_TARGET_POS)
    thing.xyzac = [1, 2, 3, 4, 5]


def a5():
    p2g.axis.NAMES = "xyza*c"
    G55.var = [0]
    tmp0 = p2g.Var(G55 * 34)
    tmp1 = p2g.Const(y=3, z=9, c=22)

    tmp0 += tmp1


def a3():
    # xyz is the default.
    G55.var = [0]
    tmp = p2g.Var(G55 * 34)


@must_be(
    "( G55.var = [0]                 )",
    "  #5241= 0.",
    "  #5242= 0.",
    "  #5243= 0.",
    "( tmp = Var[G55 * 34]           )",
    "  #100= #5241 * 34.",
    "  #101= #5242 * 34.",
    "  #102= #5243 * 34.",
    "( G55.var = [0]                 )",
    "  #5241= 0.",
    "  #5242= 0.",
    "  #5243= 0.",
    "  #5244= 0.",
    "  #5245= 0.",
    "  #5246= 0.",
    "( tmp0 = Var[G55 * 34]          )",
    "  #103= #5241 * 34.",
    "  #104= #5242 * 34.",
    "  #105= #5243 * 34.",
    "  #106= #5244 * 34.",
    "  #107= #5245 * 34.",
    "  #108= #5246 * 34.",
    "( tmp0 += tmp1                  )",
    "  #104= #104 + 3.",
    "  #105= #105 + 9.",
    "  #108= #108 + 22.",
)
def test_changing_axes():
    a3()
    a5()


def test_changing_axes():
    a3()
    a5()
