import p2g

from conftest import want


# TESTS BELOW
@want(
    "O00001 (test_simple0)",
    '( assert foo == "abc"           )',
    "  ( ok )",
    "  M30",
    "%",
)
def test_simple0():
    foo = "abc"
    assert foo == "abc"


@want(
    "O00001 (test_simple1)",
    '( assert zap == "abcdef"        )',
    "  ( ok )",
    "  M30",
    "%",
)
def test_simple1():
    foo = "abc"
    bar = "def"
    zap = foo + bar
    assert zap == "abcdef"


@want(
    "O00001 (test_simple2)",
    "( v1 = Var[len[zap]]            )",
    "  #100= 6.",
    "( v2.var = v1.var               )",
    "  #101= #100",
    "  M30",
    "%",
)
def test_simple2():
    foo = "abc"
    bar = "def"
    zap = foo + bar
    v1 = p2g.Var(len(zap))
    v2 = p2g.Var()
    v2.var = v1.var


@want(
    "O00001 (test_simple3)",
    "( v1 = Var[zap[0]]              )",
    "  #100= 97.",
    "( v2.var = v1.var               )",
    "  #101= #100",
    "  M30",
    "%",
)
def test_simple3():
    foo = "abc"
    bar = "def"
    zap = foo + bar
    v1 = p2g.Var(zap[0])
    v2 = p2g.Var()
    v2.var = v1.var


@want(
    "O00001 (test_simple4)",
    '( v1["a"] = 9                   )',
    "  #['a' + 100]= 9.",
    "  M30",
    "%",
)
def test_simple4():
    v1 = p2g.Var[10]()
    v1["a"] = 9
