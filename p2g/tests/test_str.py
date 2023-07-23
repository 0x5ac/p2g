#! ha , strings for gcode.

import p2g


@p2g.must_be()
def test_simple0():
    foo = "abc"
    assert foo == "abc"


@p2g.must_be()
def test_simple1():
    foo = "abc"
    bar = "def"
    zap = foo + bar
    assert zap == "abcdef"


@p2g.must_be(
    "( v1 = pVar[len[zap]]           )",
    "  #100= 6.                    ",
    "( v2.var = v1.var               )",
    "  #101= #100                  ",
)
def test_simple2():
    foo = "abc"
    bar = "def"
    zap = foo + bar
    v1 = p2g.Var(len(zap))
    v2 = p2g.Var()
    v2.var = v1.var


@p2g.must_be(
    "( v1 = pVar[zap[0]]             )",
    "  #100= 97.                   ",
    "( v2.var = v1.var               )",
    "  #101= #100                  ",
)
def test_simple3():
    foo = "abc"
    bar = "def"
    zap = foo + bar
    v1 = p2g.Var(zap[0])
    v2 = p2g.Var()
    v2.var = v1.var


@p2g.must_be(
    "( v1['a'] = 9                   )",
    "  #['a' + 100]= 9.            ",
)
def test_simple4():
    v1 = p2g.Var[10]()
    v1["a"] = 9
