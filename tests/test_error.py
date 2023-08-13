# noqa: F821


import p2g

from conftest import want


PROBE = p2g.Fixed[3](addr=5061)


# special case which runs all the way through the error
# machine.


# special case which runs all the way through the error
# machine.

# TESTS BELOW
########################################
@want(
    errors=[
        "test_error.py:9:4:5:     a, b = (1,)  # type: ignore",
        "                         ^                        ",
        "Not enough values to unpack.                      ",
    ]
)
def test_cerror_test_tupl1():
    #    with pytest.raises(SyntaxError, match="Not enough .*"):
    a, b = (1,)  # type: ignore
    a += a  # type: ignore
    b += b  # type: ignore


########################################
@want(
    errors=[
        "test_error.py:7:20:21:     p2g.sys.address(9)     ",
        "Only vectors have addresses.               ^      ",
    ]
)
def test_cerror_addressof0():
    p2g.sys.address(9)


########################################
@want(
    errors=[
        "test_error.py:8:24:25:     p2g.sys.address(9 + x) ",
        "Only vectors have addresses.                   ^  ",
    ]
)
def test_cerror_addressof1():
    x = p2g.haas.PROBE
    p2g.sys.address(9 + x)


########################################
@want(
    errors=[
        "test_error.py:8:6:7:     a[3][4] = 7  # type: ignore",
        "list index out of range    ^                      ",
    ]
)
def test_cerror_bad_var():
    a = []  # type: ignore
    a[3][4] = 7  # type: ignore


########################################
@want(
    errors=[
        "test_error.py:8:4:12:     try:                    ",
        "                          ^^^^^^^^                ",
        "Feature 'try' not implemented.                    ",
    ]
)
def test_cerror_no_try():
    try:
        x = 9
    except Exception:
        pass
    x = x


########################################
@want(
    errors=[
        "test_error.py:9:4:7:     p2g.haas.PROBE.fish = 100",
        "                         ^^^                      ",
        "Bad axis letter in 'fish'.                        ",
    ]
)
def test_cerror_some_errors0():
    #    with pytest.raises(AttributeError):
    p2g.haas.PROBE.fish = 100


########################################
@want(
    errors=[
        "test_error.py:8:7:8:     a, b = (1, 2, 3)  # type: ignore",
        "Too many values to unpack.  ^                     ",
    ]
)
def test_cerror_tupl0():
    #    with pytest.raises(SyntaxError, match="Too many .*"):
    a, b = (1, 2, 3)  # type: ignore
    a += a  # type: ignore
    b += b  # type: ignore


########################################
@want(
    errors=[
        "test_error.py:9:10:19:     tmp = undefined  # type: ignore # noqa: F821",
        "                                 ^^^^^^^^^        ",
        "Name 'undefined' is not defined.                  ",
    ]
)
def test_cerror_undef0():
    #    with pytest.raises(SyntaxError, match="undefined.*"):
    tmp = undefined  # type: ignore # noqa: F821
    tmp += tmp


########################################
@want(
    "O00001 (test_forcefail)                           ",
    "( haas.PROBE.x = 9              )                 ",
    "  #5061= 9.                                       ",
    '(  "quote escape" )                               ',
    "  M30                                             ",
    "%                                                 ",
)
def test_forcefail():
    p2g.haas.PROBE.x = 9
    p2g.com(' "quote escape"')
