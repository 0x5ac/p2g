#! /usr/bin/env python


import p2g as p2g


TMP = p2g.Fixed[2](addr=400)


def withv2(a, b, /, x, q=19, *, z, **za):
    pass


# crashes pytest
# @p2g.check_golden()
# def test_baddup(a, a, a):
#     pass


def withv3(*args):
    pass


def with0():
    pass


def with1(x):
    pass


def withv1(x, *, p, q):
    pass


@p2g.must_be(
    "bad arguments",
    "p2g/tests/test_func.py:7:16:17:     with0(1, 2, 3)",
    "                                                ^",
)
def test_cerror_bad_args0():
    with0(1, 2, 3)


@p2g.must_be(
    "Missing argument x",
    "p2g/tests/test_func.py:7:4:9:     with1()",
    "                                  ^^^^^",
)
def test_cerror_bad_args1():
    with1()


@p2g.must_be(
    "bad arguments",
    "p2g/tests/test_func.py:7:13:14:     with1(1, 2)",
    "                                             ^",
)
def test_cerror_bad_args2():
    with1(1, 2)


@p2g.must_be(
    "bad arguments",
    "p2g/tests/test_func.py:7:22:23:     with0(1, 2, 3, 2, 1)",
    "                                                      ^",
)
def test_cerror_bad_argsk0():
    with0(1, 2, 3, 2, 1)


@p2g.must_be(
    "bad arguments",
    "p2g/tests/test_func.py:7:23:24:     withv2(1, 2, 3, 2, 1)",
    "                                                       ^",
)
def test_cerror_bad_argsk1():
    withv2(1, 2, 3, 2, 1)


@p2g.must_be()
def test_cerror_bad_argsk2():
    withv3(1, 2, 3, 2, 1)


@p2g.must_be(
    "t0 is not defined.",
    "p2g/tests/test_func.py:7:4:6:     t0(foo=100, bar=7)",
    "                                  ^^",
)
def test_cerror_kwonly0():
    t0(foo=100, bar=7)
    t0(foo=100)


@p2g.must_be(
    "Missing argument z",
    "p2g/tests/test_func.py:7:16:17:     withv2(1, q=7)",
    "                                                ^",
)
def test_cerror_more_args0():
    withv2(1, q=7)


@p2g.must_be(
    "Missing argument z",
    "p2g/tests/test_func.py:7:18:19:     withv2(1, zap=7)",
    "                                                  ^",
)
def test_cerror_more_args1():
    withv2(1, zap=7)


@p2g.must_be(
    "Missing argument z",
    "p2g/tests/test_func.py:7:17:18:     withv2(1, za=3)",
    "                                                 ^",
)
def test_cerror_more_args2():
    withv2(1, za=3)


@p2g.must_be(
    "Missing argument x",
    "p2g/tests/test_func.py:7:15:16:     withv2(za9=3)",
    "                                               ^",
)
def test_cerror_more_args3():
    withv2(za9=3)


@p2g.must_be(
    "ins1 is not defined.",
    "p2g/tests/test_func.py:8:4:8:     ins1(T)",
    "                                  ^^^^",
)
def test_cerror_nesting_functions1():
    T = p2g.Var()
    ins1(T)


@p2g.must_be(
    "inside2 is not defined.",
    "p2g/tests/test_func.py:8:4:11:     inside2(T[0], T[1])",
    "                                   ^^^^^^^",
)
def test_cerror_nesting_functions2():
    T = p2g.Var[2]()
    inside2(T[0], T[1])


@p2g.must_be(
    "inside3 is not defined.",
    "p2g/tests/test_func.py:9:4:11:     inside3(T[0], T[1], V)",
    "                                   ^^^^^^^",
)
def test_cerror_nesting_functions3():
    T = p2g.Var[2]()
    V = p2g.Const(1, 2, 3)
    inside3(T[0], T[1], V)


@p2g.must_be(
    "t1 is not defined.",
    "p2g/tests/test_func.py:7:4:6:     t1(0, 1)",
    "                                  ^^",
)
def test_cerror_varargs0():
    t1(0, 1)


@p2g.must_be(
    "t1 is not defined.",
    "p2g/tests/test_func.py:7:4:6:     t1(zap=123, dog=999)",
    "                                  ^^",
)
def test_cerror_varargs1():
    t1(zap=123, dog=999)


@p2g.must_be(
    "t1 is not defined.",
    "p2g/tests/test_func.py:7:4:6:     t1(zap=123)",
    "                                  ^^",
)
def test_cerror_varargs2():
    t1(zap=123)


def callunp(**fish):
    T = p2g.Var[2]()
    T[0] = fish["fish"]


@p2g.must_be(
    '( T[0] = fish["fish"]           )',
    "  #100= 98.",
)
def test_unpack0():
    x = {"fish": 98}
    callunp(**x)


def callunp1(fish=3):
    T = p2g.Var[2]()
    T[0] = fish["fish"]


@p2g.must_be(
    "bad arguments.",
    "p2g/tests/test_func.py:8:15:16:     callunp1(**x)",
    "                                               ^",
)
def test_cerror_unpack1():
    x = {"zap": 98}
    callunp1(**x)


@p2g.must_be(
    "DPRNT[this*is*19.00]",
)
def test_dprint2():
    x = 19
    p2g.dprint(f"this is {x:5.2f}")


@p2g.must_be(
    "( xc = Var[12]                  )",
    "  #100= 12.",
    "DPRNT[this*is*[#100][52]]",
)
def test_dprint3():
    xc = p2g.Var(12)
    p2g.dprint(f"this is {xc:5.2f}")


@p2g.must_be(
    "( xc = Var[12]                  )",
    "  #100= 12.",
    "DPRNT[this*is*[#100+#100][52]]",
)
def test_dprint4():
    xc = p2g.Var(12)
    p2g.dprint(f"this is {xc+xc:5.2f}")
