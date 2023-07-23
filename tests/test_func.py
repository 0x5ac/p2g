import p2g as p2g

from conftest import want


TMP = p2g.Fixed[2](addr=400)


def withv2(a, b, /, x, q=19, *, z, **za):
    pass


def withv3(*args):
    pass


def with0():
    pass


def with1(x):
    pass


def withv1(x, *, p, q):
    pass


def callunp(**fish):
    T = p2g.Var[2]()
    T[0] = fish["fish"]


def callunp1(fish=3):
    T = p2g.Var[2]()
    T[0] = fish["fish"]  # type: ignore


# TESTS BELOW
@want(
    errors=[
        "Too many arguments; 3 > 0.                        ",
        "tests/test_func.py:9:16:17:     with0(1, 2, 3)  # type: ignore",
        "                                            ^     ",
    ]
)
def test_cerror_bad_args0():
    with0(1, 2, 3)  # type: ignore


@want(
    errors=[
        "Missing argument 'x'.                             ",
        "tests/test_func.py:9:4:9:     with1()  # type: ignore",
        "                              ^^^^^               ",
    ]
)
def test_cerror_bad_args1():
    with1()  # type: ignore


@want(
    errors=[
        "Too many arguments; 2 > 1.                        ",
        "tests/test_func.py:9:13:14:     with1(1, 2)  # type: ignore",
        "                                         ^        ",
    ]
)
def test_cerror_bad_args2():
    with1(1, 2)  # type: ignore


@want(
    errors=[
        "Too many arguments; 5 > 0.                        ",
        "tests/test_func.py:9:22:23:     with0(1, 2, 3, 2, 1)  # type: ignore",
        "                                                  ^",
    ]
)
def test_cerror_bad_argsk0():
    with0(1, 2, 3, 2, 1)  # type: ignore


@want(
    errors=[
        "Too many arguments; 5 > 2.                        ",
        "tests/test_func.py:9:23:24:     withv2(1, 2, 3, 2, 1)  # type: ignore",
        "                                                   ^",
    ]
)
def test_cerror_bad_argsk1():
    withv2(1, 2, 3, 2, 1)  # type: ignore


@want(
    "O00001 (test_cerror_bad_argsk2)",
    "  M30",
    "%",
)
def test_cerror_bad_argsk2():
    withv3(1, 2, 3, 2, 1)


@want(
    errors=[
        "Name 'undefined' is not defined.                  ",
        "tests/test_func.py:9:4:13:     undefined(foo=100, bar=7)  # type: ignore # noqa: F821",
        "                               ^^^^^^^^^          ",
    ]
)
def test_cerror_kwonly0():
    undefined(foo=100, bar=7)  # type: ignore # noqa: F821
    undefined(foo=100)  # type: ignore  # noqa: F821


@want(
    errors=[
        "Missing argument 'z'.                             ",
        "tests/test_func.py:9:16:17:     withv2(1, q=7)  # type: ignore",
        "                                            ^     ",
    ]
)
def test_cerror_more_args0():
    withv2(1, q=7)  # type: ignore


@want(
    errors=[
        "Missing argument 'z'.                             ",
        "tests/test_func.py:9:18:19:     withv2(1, zap=7)  # type: ignore",
        "                                              ^   ",
    ]
)
def test_cerror_more_args1():
    withv2(1, zap=7)  # type: ignore


@want(
    errors=[
        "Missing argument 'z'.                             ",
        "tests/test_func.py:9:17:18:     withv2(1, za=3)  # type: ignore",
        "                                             ^    ",
    ]
)
def test_cerror_more_args2():
    withv2(1, za=3)  # type: ignore


@want(
    errors=[
        "Missing argument 'x'.                             ",
        "tests/test_func.py:9:15:16:     withv2(za9=3)  # type: ignore",
        "                                           ^      ",
    ]
)
def test_cerror_more_args3():
    withv2(za9=3)  # type: ignore


@want(
    errors=[
        "Name 'undefined' is not defined.                  ",
        "tests/test_func.py:10:4:13:     undefined(T)  # type: ignore  # noqa: F821",
        "                                ^^^^^^^^^         ",
    ]
)
def test_cerror_nesting_functions1():
    T = p2g.Var()
    undefined(T)  # type: ignore  # noqa: F821


@want(
    errors=[
        "Name 'undefined' is not defined.                  ",
        "tests/test_func.py:10:4:13:     undefined(T[0], T[1])  # type: ignore  # noqa: F821",
        "                                ^^^^^^^^^         ",
    ]
)
def test_cerror_nesting_functions2():
    T = p2g.Var[2]()
    undefined(T[0], T[1])  # type: ignore  # noqa: F821


@want(
    errors=[
        "Name 'undefined' is not defined.                  ",
        "tests/test_func.py:11:4:13:     undefined(T[0], T[1], V)  # type: ignore  # noqa: F821",
        "                                ^^^^^^^^^         ",
    ]
)
def test_cerror_nesting_functions3():
    T = p2g.Var[2]()
    V = p2g.Const(1, 2, 3)
    undefined(T[0], T[1], V)  # type: ignore  # noqa: F821


@want(
    errors=[
        "Bad arguments.                                    ",
        "tests/test_func.py:10:15:16:     callunp1(**x)    ",
        "                                            ^     ",
    ]
)
def test_cerror_unpack1():
    x = {"zap": 98}
    callunp1(**x)


@want(
    errors=[
        "Name 'undefined' is not defined.                  ",
        "tests/test_func.py:9:4:13:     undefined(0, 1)  # type: ignore  # noqa: F821",
        "                               ^^^^^^^^^          ",
    ]
)
def test_cerror_varargs0():
    undefined(0, 1)  # type: ignore  # noqa: F821


@want(
    errors=[
        "Name 'undefined' is not defined.                  ",
        "tests/test_func.py:9:4:13:     undefined(zap=123, dog=999)  # type: ignore  # noqa: F821",
        "                               ^^^^^^^^^          ",
    ]
)
def test_cerror_varargs1():
    undefined(zap=123, dog=999)  # type: ignore  # noqa: F821


@want(
    errors=[
        "Name 'undefined' is not defined.                  ",
        "tests/test_func.py:9:4:13:     undefined(zap=123)  # type: ignore # noqa: F821",
        "                               ^^^^^^^^^          ",
    ]
)
def test_cerror_varargs2():
    undefined(zap=123)  # type: ignore # noqa: F821


@want(
    "O00001 (test_dprint2)",
    "DPRNT[this*is*19.00]",
    "  M30",
    "%",
)
def test_dprint2():
    x = 19
    p2g.dprint(f"this is {x:5.2f}")


@want(
    "O00001 (test_dprint3)",
    "( xc = Var[12]                  )",
    "  #100= 12.",
    "DPRNT[this*is*[#100][52]]",
    "  M30",
    "%",
)
def test_dprint3():
    xc = p2g.Var(12)
    p2g.dprint(f"this is {xc:5.2f}")


@want(
    "O00001 (test_dprint4)",
    "( xc = Var[12]                  )",
    "  #100= 12.",
    "DPRNT[this*is*[#100+#100][52]]",
    "  M30",
    "%",
)
def test_dprint4():
    xc = p2g.Var(12)
    p2g.dprint(f"this is {xc+xc:5.2f}")


@want(
    "O00001 (test_unpack0)",
    '( T[0] = fish["fish"]           )',
    "  #100= 98.",
    "  M30",
    "%",
)
def test_unpack0():
    x = {"fish": 98}
    callunp(**x)
