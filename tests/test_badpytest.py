import io
import sys

from p2g.main import main


# can't be tested by directly pytest becase fail import.


def must_fail(cap, intxt, errmsg):
    sys.stdin = io.StringIO("\n".join(intxt))

    main(["-"])
    assert errmsg in cap.readouterr().err


def test_cerror_nonlocal8(capfd):
    must_fail(
        capfd,
        [
            "def t1():",
            "  nonlocal fish",
            "  fish = 3",
        ],
        "No binding for nonlocal 'fish'",
    )


def test_cerror_global1(capfd):
    must_fail(
        capfd,
        [
            "def t1():",
            "  fish = 3",
            "  global fish",
        ],
        "Name 'fish' before global",
    )


def test_cerror_nonlocal2(capfd):
    must_fail(
        capfd,
        [
            "nonlocal xyz",
            "def test_cerror_nonlocal_at_top():",
            "  pass",
        ],
        "'nonlocal' declaration not allowed at module level",
    )


def test_cerror_nonlocal3(capfd):
    must_fail(
        capfd,
        [
            "def p(): return 7",
            "def zz():",
            "       nonlocal p",
            "       p = 3",
            "zz()",
        ],
        "No binding for nonlocal 'p'.",
    )


def test_cerror_return(capfd):
    must_fail(
        capfd,
        [
            "return",
        ],
        "'return' outside function.",
    )


# TESTS BELOW
