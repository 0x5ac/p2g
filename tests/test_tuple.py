# mypy: disable-error-code="misc"
import p2g

from conftest import want


V = p2g.Fixed[4](addr=100)
W = p2g.Fixed[4](addr=200)

# TESTS BELOW


@want(
    errors=[
        "Not enough values to unpack.                      ",
        "tests/test_tuple.py:9:7:8:     a, b, c = (1, 2)  # noqa: F841",
        "                                  ^               ",
    ]
)
def test_cerror_too_few_xfail():
    a, b, c = (1, 2)  # noqa: F841


@want(
    errors=[
        "Too many values to unpack.                        ",
        "tests/test_tuple.py:9:10:11:     a, b, c = (1, 2, 3, 4)  # noqa: F841",
        "                                       ^          ",
    ]
)
def test_cerror_too_many():
    a, b, c = (1, 2, 3, 4)  # noqa: F841


@want(
    "O00001 (test_tupl0)",
    "( V[0:3] = [1, 2, 3]            )",
    "  #100= 1.",
    "  #101= 2.",
    "  #102= 3.",
    "  M30",
    "%",
)
def test_tupl0():
    V[0:3] = (1, 2, 3)


@want(
    "O00001 (test_tupl1)",
    "( V[0], V[2] = [1, 2]           )",
    "  #100= 1.",
    "  #102= 2.",
    "  M30",
    "%",
)
def test_tupl1():
    V[0], V[2] = (1, 2)


@want(
    "O00001 (test_tupl2)",
    "( V[0], V[2] = W[0], W[1]       )",
    "  #100= #200",
    "  #102= #201",
    "  M30",
    "%",
)
def test_tupl2():
    V[0], V[2] = W[0], W[1]


@want(
    "O00001 (test_tupl3)",
    "( V[0:3] = [h, tl[0], tl[1]]    )",
    "  #100= 1.",
    "  #101= 2.",
    "  #102= 3.",
    "  M30",
    "%",
)
def test_tupl3():
    h, *tl = [1, 2, 3]
    V[0:3] = (h, tl[0], tl[1])
