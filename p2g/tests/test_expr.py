import p2g


@p2g.must_be(
    "( v[0] = v[1] if v[2] else v[3] )",
    "  #100= #101 * [#102 NE 0.] + #103 * [#102 EQ 0.]",
)
def test_ifelse():
    v = p2g.Fixed[10](addr=100)

    v[0] = v[1] if v[2] else v[3]


@p2g.must_be(
    "( v[0] = j - v[1]               )",
    "  #100= 1. - #101             ",
)
def test_rsub1():
    v = p2g.Fixed[10](addr=100)
    j = 1
    v[0] = j - v[1]


@p2g.must_be(
    "( v[0] = 1.0 - v[2]             )",
    "  #100= 1. - #102             ",
)
def test_rsub2():
    v = p2g.Fixed[10](addr=100)

    v[0] = 1.0 - v[2]


@p2g.must_be(
    "( v[0] = 1.0 - 2.0              )",
    "  #100= -1.                   ",
)
def test_rsub():
    v = p2g.Fixed[10](addr=100)

    v[0] = 1.0 - 2.0
