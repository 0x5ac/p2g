import pytest

import p2g

from p2g.ptest import must_be


PROBE = p2g.Fixed[3](addr=5061)


# special case which runs all the way through the error
# machine.


# special case which runs all the way through the error
# machine.


def fish():
    PROBE.x = 9


@pytest.mark.xfail
@must_be(
    "( PROBE.x = 9                   )",
    " error  #5061= 9.",
    '(  "quote escape" )',
)
def test_forcefail():
    PROBE.x = 9
    p2g.com(' "quote escape"')


@must_be(
    "Can only take address of something with location.",
    "p2g/tests/test_error.py:7:20:21:     f = p2g.address(9)",
    "                                                     ^",
)
def test_cerror_addressof0():
    f = p2g.address(9)


@must_be(
    "Can only take address of something with location.",
    "p2g/tests/test_error.py:8:24:25:     f = p2g.address(9 + x)",
    "                                                         ^",
)
def test_cerror_addressof1():
    x = PROBE
    f = p2g.address(9 + x)


@must_be(
    "list index out of range",
    "p2g/tests/test_error.py:8:6:7:     a[3][4] = 7",
    "                                     ^",
)
def test_cerror_bad_var():
    a = []
    a[3][4] = 7


@must_be(
    "Not enough values to unpack.",
    "p2g/tests/test_error.py:8:4:5:     a, b = (1,)",
    "                                   ^",
)
def test_cerror_test_tupl1():
    #    with pytest.raises(SyntaxError, match="Not enough .*"):
    a, b = (1,)


@must_be(
    "Feature 'try' not implemented.",
    "p2g/tests/test_error.py:7:4:12:     try:",
    "                                    ^^^^^^^^",
)
def test_cerror_no_try():
    try:
        fish()
    except Exception:
        pass


@must_be(
    "Bad axis letter in 'fish'.",
    "p2g/tests/test_error.py:8:4:9:     PROBE.fish = 100",
    "                                   ^^^^^",
)
def test_cerror_some_errors0():
    #    with pytest.raises(AttributeError):
    PROBE.fish = 100


@must_be(
    "Too many values to unpack.",
    "p2g/tests/test_error.py:8:7:8:     a, b = (1, 2, 3)",
    "                                      ^",
)
def test_cerror_tupl0():
    #    with pytest.raises(SyntaxError, match="Too many .*"):
    a, b = (1, 2, 3)


@must_be(
    "Name 'undefined' is not defined.",
    "p2g/tests/test_error.py:8:10:19:     tmp = undefined",
    "                                           ^^^^^^^^^",
)
def test_cerror_undef0():
    #    with pytest.raises(SyntaxError, match="undefined.*"):
    tmp = undefined


@must_be(
    "Feature 'try' not implemented.",
    "p2g/tests/test_error.py:7:4:12:     try:",
    "                                 ^^^^^^^^",
)
def test_cerror_no_try():
    try:
        fish()
    except Exception:
        pass


@pytest.mark.xfail()
@must_be("b")
def test_cerror_assert0():
    assert False


@pytest.mark.xfail()
@must_be("a")
def test_cerror_assert1():
    assert False, "message"
