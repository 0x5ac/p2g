import pytest

import p2g


PROBE = p2g.Fixed[3](addr=5061)


# special case which runs all the way through the error
# machine.


# special case which runs all the way through the error
# machine.


def fish():
    PROBE.x = 9


@pytest.mark.forcefail
@p2g.must_be("not the right answer")
def test_forcefail():
    PROBE.x = 9
    p2g.com(' "quote escape"')


@pytest.mark.forcefail
@p2g.check_golden()
def test_forcefail1():
    PROBE.x = 9
    p2g.com(' "quote escape"')


@p2g.must_be(
    "Can only take address of something with location.",
    "p2g/tests/test_error.py:7:20:21:     f = p2g.address(9)",
    "                                                     ^",
)
def test_comperr_addressof0():
    f = p2g.address(9)


@p2g.must_be(
    "Can only take address of something with location.",
    "p2g/tests/test_error.py:8:24:25:     f = p2g.address(9 + x)",
    "                                                         ^",
)
def test_comperr_addressof1():
    x = PROBE
    f = p2g.address(9 + x)


@p2g.must_be(
    "list index out of range",
    "p2g/tests/test_error.py:8:6:7:     a[3][4] = 7",
    "                                     ^",
)
def test_comperr_bad_var():
    a = []
    a[3][4] = 7


@p2g.must_be(
    "Not enough values to unpack.",
    "p2g/tests/test_error.py:8:4:5:     a, b = (1,)",
    "                                   ^",
)
def test_comperr_test_tupl1():
    #    with pytest.raises(SyntaxError, match="Not enough .*"):
    a, b = (1,)


@p2g.must_be(
    "Try not implemented",
    "p2g/tests/test_error.py:7:4:12:     try:",
    "                                    ^^^^^^^^",
)
def test_comperr_no_try():
    try:
        fish()
    except Exception:
        pass


@p2g.must_be(
    "Redefinition of a.",
    "p2g/tests/test_error.py:9:4:6:     st.a = 10",
    "                                   ^^",
)
def test_comperr_redef():
    st = p2g.Symbols()
    st.a = 9
    st.a = 10


@p2g.must_be(
    "Bad axis letter in 'fish'",
    "p2g/tests/test_error.py:8:4:9:     PROBE.fish = 100",
    "                                   ^^^^^",
)
def test_comperr_some_errors0():
    #    with pytest.raises(AttributeError):
    PROBE.fish = 100


@p2g.must_be(
    "Too many values to unpack.",
    "p2g/tests/test_error.py:8:7:8:     a, b = (1, 2, 3)",
    "                                      ^",
)
def test_comperr_tupl0():
    #    with pytest.raises(SyntaxError, match="Too many .*"):
    a, b = (1, 2, 3)


@p2g.must_be(
    "undefined is not defined.",
    "p2g/tests/test_error.py:8:10:19:     tmp = undefined",
    "                                           ^^^^^^^^^",
)
def test_comperr_undef0():
    #    with pytest.raises(SyntaxError, match="undefined.*"):
    tmp = undefined


@p2g.must_be(
    "Try not implemented",
    "p2g/tests/test_error.py:7:4:12:     try:",
    "                                 ^^^^^^^^",
)
def test_comperr_no_try():
    try:
        fish()
    except Exception:
        pass


@p2g.must_be()
@pytest.mark.xfail()
def test_xfail_assert0():
    assert False


@p2g.must_be()
@pytest.mark.xfail()
def test_xfail_assert1():
    assert False, "message"
