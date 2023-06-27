import p2g

from p2g.ptest import must_be


# from p2g.tests.test_error import fish


class Fish:
    j = 9
    p = j + 3


num = 123

PR = p2g.Fixed(191, 200 + 3, addr=402)


@must_be(
    "( PR = Fixed[191, 200 + 3, addr=402])",
    "  #402= 191.                  ",
    "  #403= 203.",
    "( dst[0] = num                  )",
    "  #302= 123.                  ",
    "",
)
def test_global0():
    dst = p2g.Fixed(addr=302)
    dst[0] = num


@must_be(
    "( PR = Fixed[191, 200 + 3, addr=402])",
    "  #402= 191.                  ",
    "  #403= 203.",
    "( PR[0] = num                   )",
    "  #402= 123.                  ",
    "",
)
def test_global1():
    PR[0] = num


@must_be(
    "( PR = Fixed[191, 200 + 3, addr=402])",
    "  #402= 191.                  ",
    "  #403= 203.",
    "( PR[0] = num                   )",
    "  #402= 17.                   ",
    "",
)
def test_global2():
    global num
    num = 17
    PR[0] = num


@must_be(
    "( PR = Fixed[191, 200 + 3, addr=402])",
    "  #402= 191.                  ",
    "  #403= 203.",
    "",
)
def test_global3():
    global num
    del num


@must_be(
    "( PR = Fixed[191, 200 + 3, addr=402])",
    "  #402= 191.",
    "  #403= 203.",
    "( dst[0] = 123                  )",
    "  #300= 123.",
    "(     dst[0] = 456              )",
    "  #301= 456.",
)
def test_local():
    dst = p2g.Fixed(addr=300)
    dst[0] = 123

    def inner():
        dst = p2g.Fixed(addr=301)
        dst[0] = 456

    inner()


@must_be(
    "( PR = Fixed[191, 200 + 3, addr=402])",
    "  #402= 191.                  ",
    "  #403= 203.",
    "( dst[0] = 123                  )",
    "  #300= 123.                  ",
    "(     dst[0] = 456              )",
    "  #300= 456.                  ",
    "",
)
def test_nonlocal():
    dst = p2g.Fixed(addr=300)
    dst[0] = 123

    def inner():
        nonlocal dst
        dst[0] = 456

    inner()


@must_be(
    "( PR = Fixed[191, 200 + 3, addr=402])",
    "  #402= 191.                  ",
    "  #403= 203.",
    "( dst[0] = 123                  )",
    "  #300= 123.                  ",
    "(     dst[0] = 456              )",
    "  #300= 456.                  ",
    "",
)
def test_nonlocal1():
    dst = p2g.Fixed(addr=300)
    dst[0] = 123

    def inner():
        nonlocal dst
        dst[0] = 456
        del dst

    inner()


@must_be(
    "Name 'inner' is not defined.",
    "p2g/tests/test_vars.py:10:4:9:     inner()",
    "                                   ^^^^^",
)
def test_cerror_nonlocal2():
    dst = p2g.Fixed(addr=300)
    dst[0] = 123

    inner()


j = 129


@must_be(
    "( PR = Fixed[191, 200 + 3, addr=402])",
    "  #402= 191.                  ",
    "  #403= 203.",
    "",
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
            j = 1

        in2()

    in1()


@must_be(
    "Name 'nothing' is not defined.",
    "p2g/tests/test_vars.py:7:8:15:     del nothing",
    "                                       ^^^^^^^",
)
def test_cerror_novar0():
    del nothing


@must_be(
    "( PR = Fixed[191, 200 + 3, addr=402])",
    "  #402= 191.",
    "  #403= 203.",
    "( x.var = zap[]                 )",
    "  #100= 33.",
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


global q
q = 87


@must_be(
    "( PR = Fixed[191, 200 + 3, addr=402])",
    "  #402= 191.",
    "  #403= 203.",
    "(     x.var = q                 )",
    "  #100= 2.",
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


j = 32


@must_be(
    "( PR = Fixed[191, 200 + 3, addr=402])",
    "  #402= 191.",
    "  #403= 203.",
)
def test_nonlocal7():
    __name__ = 3

    def foop():
        nonlocal __name__
        j += 12

        def zap():
            global __name__
            j += __name__

        zap()

    foop()
