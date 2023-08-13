import io
import sys
import pathlib
from p2g.main import main


# can't be tested by directly pytest becase fail import.


def gotlines(cap):
    # if split at newlines, then get an extra
    # line at the end which we kill
    return cap.readouterr().err.split("\n")[:-1]


def must_fail(cap, *, src=[], want=[]):

    sys.stdin = io.StringIO("\n".join(src))
    main(["--short-filenames", "-"])

    got = gotlines(cap)

    assert got == want


def test_cerror_nonlocal8(capfd):
    must_fail(
        capfd,
        src=[
            "def t1():",
            "  nonlocal fish",
            "  fish = 3",
        ],
        want=[
            "-:3:2:6:   fish = 3",
            "           ^^^^",
            "No binding for nonlocal 'fish'.",
        ],
    )


def test_cerror_return(capfd):
    must_fail(
        capfd,
        src=[
            "return",
        ],
        want=[
            "-:1:0:6: return",
            "         ^^^^^^",
            "'return' outside function.",
        ],
    )


def test_cerror_global1(capfd):
    must_fail(
        capfd,
        src=[
            "def t1():",
            "  fish = 3",
            "  global fish",
        ],
        want=[
            "-:3:2:13:   global fish",
            "            ^^^^^^^^^^^",
            "Name 'fish' before global.",
        ],
    )


def test_cerror_nonlocal2(capfd):
    must_fail(
        capfd,
        src=[
            "nonlocal  xyz",
            "def test_cerror_nonlocal_at_top():",
            "  pass",
        ],
        want=[
            "-:1:0:13: nonlocal  xyz",
            "          ^^^^^^^^^^^^^",
            "'nonlocal' declaration not allowed at module level.",
        ],
    )


def test_cerror_nonlocal3(capfd):
    must_fail(
        capfd,
        src=[
            "def p(): return 7",
            "def zz():",
            "       nonlocal p",
            "       p = 3",
            "zz()",
        ],
        want=[
            "-:4:7:8:        p = 3",
            "                ^",
            "No binding for nonlocal 'p'.",
        ],
    )


# TESTS BELOW
