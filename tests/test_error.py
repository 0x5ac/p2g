# noqa: F821


import p2g

from conftest import want


PROBE = p2g.Fixed[3](addr=5061)


# special case which runs all the way through the error
# machine.


# special case which runs all the way through the error
# machine.

# TESTS BELOW
@want(
    errors=[
        "Only vectors have addresses.                      ",
        "tests/test_error.py:9:16:17:     p2g.address(9)   ",
        "                                             ^    ",
    ]
)
def test_cerror_addressof0():
    p2g.address(9)


@want(
    errors=[
        "Only vectors have addresses.                      ",
        "tests/test_error.py:10:20:21:     p2g.address(9 + x)",
        "                                                  ^",
    ]
)
def test_cerror_addressof1():
    x = PROBE
    p2g.address(9 + x)


@want(
    errors=[
        "list index out of range                           ",
        "tests/test_error.py:10:6:7:     a[3][4] = 7  # type: ignore",
        "                                  ^               ",
    ]
)
def test_cerror_bad_var():
    a = []  # type: ignore
    a[3][4] = 7  # type: ignore


@want(
    errors=[
        "Feature 'try' not implemented.                    ",
        "tests/test_error.py:9:4:12:     try:              ",
        "                                ^^^^^^^^          ",
    ]
)
def test_cerror_no_try():
    try:
        x = 9
    except Exception:
        pass
    x = x


@want(
    errors=[
        "Bad axis letter in 'fish'.                        ",
        "tests/test_error.py:10:4:9:     PROBE.fish = 100  ",
        "                                ^^^^^             ",
    ]
)
def test_cerror_some_errors0():
    #    with pytest.raises(AttributeError):
    PROBE.fish = 100


@want(
    errors=[
        "Not enough values to unpack.                      ",
        "tests/test_error.py:10:4:5:     a, b = (1,)  # type: ignore",
        "                                ^                 ",
    ]
)
def test_cerror_test_tupl1():
    #    with pytest.raises(SyntaxError, match="Not enough .*"):
    a, b = (1,)  # type: ignore
    a += a  # type: ignore
    b += b  # type: ignore


@want(
    errors=[
        "Too many values to unpack.                        ",
        "tests/test_error.py:10:7:8:     a, b = (1, 2, 3)  # type: ignore",
        "                                   ^              ",
    ]
)
def test_cerror_tupl0():
    #    with pytest.raises(SyntaxError, match="Too many .*"):
    a, b = (1, 2, 3)  # type: ignore
    a += a  # type: ignore
    b += b  # type: ignore


@want(
    errors=[
        "Name 'undefined' is not defined.                  ",
        "tests/test_error.py:10:10:19:     tmp = undefined  # type: ignore # noqa: F821",
        "                                        ^^^^^^^^^ ",
    ]
)
def test_cerror_undef0():
    #    with pytest.raises(SyntaxError, match="undefined.*"):
    tmp = undefined  # type: ignore # noqa: F821
    tmp += tmp


@want(
    "O00001 (test_forcefail)",
    "( PROBE.x = 9                   )",
    "  #5061= 9.",
    '(  "quote escape" )',
    "  M30",
    "%",
)
def test_forcefail():
    PROBE.x = 9
    p2g.com(' "quote escape"')
