import p2g


V = p2g.Fixed[4](addr=100)
W = p2g.Fixed[4](addr=200)


@p2g.must_be(
    "Not enough values to unpack.",
    "p2g/tests/test_tuple.py:7:7:8:     a, b, c = (1, 2)",
    "                                      ^",
)
def test_cerror_too_few_xfail():
    a, b, c = (1, 2)


@p2g.must_be(
    "Too many values to unpack.",
    "p2g/tests/test_tuple.py:7:10:11:     a, b, c = (1, 2, 3, 4)",
    "                                           ^",
)
def test_cerror_too_many():
    a, b, c = (1, 2, 3, 4)


@p2g.must_be(
    "( V[0:3] = [1, 2, 3]            )",
    "  #100= 1.                    ",
    "  #101= 2.",
    "  #102= 3.",
)
def test_tupl0():
    V[0:3] = (1, 2, 3)


@p2g.must_be(
    "( V[0], V[2] = [1, 2]           )",
    "  #100= 1.                    ",
    "  #102= 2.",
)
def test_tupl1():
    V[0], V[2] = (1, 2)


@p2g.must_be(
    "( V[0], V[2] = W[0], W[1]       )",
    "  #100= #200                  ",
    "  #102= #201",
)
def test_tupl2():
    V[0], V[2] = W[0], W[1]


@p2g.must_be(
    "( V[0:3] = [h, tl[0], tl[1]]    )",
    "  #100= 1.                    ",
    "  #101= 2.",
    "  #102= 3.",
)
def test_tupl3():
    h, *tl = [1, 2, 3]
    V[0:3] = (h, tl[0], tl[1])
