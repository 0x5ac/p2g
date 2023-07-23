# mypy: disable-error-code="name-defined"
import p2g

from conftest import want


# from p2g.tests.test_error import fish


class Fish:
    j = 9
    p = j + 3


num = 123

PR = p2g.Fixed(191, 200 + 3, addr=402)

j = 129

global q
q = 87
j = 32

# TESTS BELOW


@want(
    errors=[
        "Name 'undefined' is not defined.                  ",
        "tests/test_vars.py:12:4:13:     undefined()  # noqa: F821",
        "                                ^^^^^^^^^         ",
    ]
)
def test_cerror_nonlocal2():
    dst = p2g.Fixed(addr=300)
    dst[0] = 123

    undefined()  # noqa: F821


@want(
    errors=[
        "Name 'undefined' is not defined.                  ",
        "tests/test_vars.py:9:8:17:     del undefined  # noqa: F821",
        "                                   ^^^^^^^^^      ",
    ]
)
def test_cerror_novar0():
    del undefined  # noqa: F821


@want(
    "O00001 (test_global0)",
    "( PR = Fixed[191, 200 + 3, addr=402])",
    "  #402= 191.",
    "  #403= 203.",
    "( dst[0] = num                  )",
    "  #302= 123.",
    "  M30",
    "%",
)
def test_global0():
    dst = p2g.Fixed(addr=302)
    dst[0] = num


@want(
    "O00001 (test_global1)",
    "( PR = Fixed[191, 200 + 3, addr=402])",
    "  #402= 191.",
    "  #403= 203.",
    "( PR[0] = num                   )",
    "  #402= 123.",
    "  M30",
    "%",
)
def test_global1():
    PR[0] = num


@want(
    "O00001 (test_global2)",
    "( PR = Fixed[191, 200 + 3, addr=402])",
    "  #402= 191.",
    "  #403= 203.",
    "( PR[0] = num                   )",
    "  #402= 17.",
    "  M30",
    "%",
)
def test_global2():
    global num
    num = 17
    PR[0] = num


@want(
    "O00001 (test_global3)",
    "( PR = Fixed[191, 200 + 3, addr=402])",
    "  #402= 191.",
    "  #403= 203.",
    "  M30",
    "%",
)
def test_global3():
    global num
    del num


@want(
    "O00001 (test_local)",
    "( PR = Fixed[191, 200 + 3, addr=402])",
    "  #402= 191.",
    "  #403= 203.",
    "( dst[0] = 123                  )",
    "  #300= 123.",
    "(     dst[0] = 456              )",
    "  #301= 456.",
    "  M30",
    "%",
)
def test_local():
    dst = p2g.Fixed(addr=300)
    dst[0] = 123

    def inner():
        dst = p2g.Fixed(addr=301)
        dst[0] = 456

    inner()


@want(
    "O00001 (test_nonlocal)",
    "( PR = Fixed[191, 200 + 3, addr=402])",
    "  #402= 191.",
    "  #403= 203.",
    "( dst[0] = 123                  )",
    "  #300= 123.",
    "(     dst[0] = 456              )",
    "  #300= 456.",
    "  M30",
    "%",
)
def test_nonlocal():
    dst = p2g.Fixed(addr=300)
    dst[0] = 123

    def inner():
        nonlocal dst
        dst[0] = 456

    inner()


@want(
    "O00001 (test_nonlocal1)",
    "( PR = Fixed[191, 200 + 3, addr=402])",
    "  #402= 191.",
    "  #403= 203.",
    "( dst[0] = 123                  )",
    "  #300= 123.",
    "(     dst[0] = 456              )",
    "  #300= 456.",
    "  M30",
    "%",
)
def test_nonlocal1():
    dst = p2g.Fixed(addr=300)
    dst[0] = 123

    def inner():
        nonlocal dst
        dst[0] = 456
        del dst

    inner()


@want(
    "O00001 (test_nonlocal3)",
    "( PR = Fixed[191, 200 + 3, addr=402])",
    "  #402= 191.",
    "  #403= 203.",
    "  M30",
    "%",
)
def test_nonlocal3():
    global j
    k = 3

    def in1():
        k = 2
        m = j

        def in2():
            nonlocal m
            nonlocal k
            k += 1
            j = 1  # noqa: F841

        in2()

    in1()


@want(
    "O00001 (test_nonlocal5)",
    "( PR = Fixed[191, 200 + 3, addr=402])",
    "  #402= 191.",
    "  #403= 203.",
    "( x.var = zap[]                 )",
    "  #100= 33.",
    "  M30",
    "%",
)
def test_nonlocal5():
    q = 9

    def zap():
        nonlocal q
        q = q + 3

        def wee():
            nonlocal q
            q = q + 9
            return q

        return q + wee()

    x = p2g.Var()
    x.var = zap()


@want(
    "O00001 (test_nonlocal6)",
    "( PR = Fixed[191, 200 + 3, addr=402])",
    "  #402= 191.",
    "  #403= 203.",
    "(     x.var = q                 )",
    "  #100= 2.",
    "  M30",
    "%",
)
def test_nonlocal6():
    q = 2

    def pop():
        global q
        q = 3

    def zap():
        nonlocal q
        x = p2g.Var()
        x.var = q

    pop()
    zap()


@want(
    "O00001 (test_nonlocal7)",
    "( PR = Fixed[191, 200 + 3, addr=402])",
    "  #402= 191.",
    "  #403= 203.",
    "  M30",
    "%",
)
def test_nonlocal7():
    __name__ = 3

    def foop():
        nonlocal __name__
        j += 12  # noqa: F823

        def zap():
            global __name__
            j += len(__name__)  # noqa: F823, F841

        zap()

    foop()
