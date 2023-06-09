from p2g import *
from p2g.ptest import must_be


@must_be(
    "( for i in range[10]:           )",
    "  #101= 0.",
    "N1000",
    "  IF [#101 GE 10.] GOTO 1002",
    "DPRNT[got*[#101]]",
    '(     dprint[f"got {i}"]        )',
    "  #101= #101 + 1.",
    "  GOTO 1000",
    "N1002",
)
def test_for0():
    for i in range(10):
        dprint(f"got {i}")


@must_be(
    "Must be simple name as destination for 'for'.",
    "tests/test_for.py:8:23:25:     for i.var in range(10):",
    "                                                       ^^",
)
def test_cerror_for1():
    i = Var()
    for i.var in range(10):
        dprint(f"got {i.var}")


@must_be(
    "( fish )",
    "( for x in range[1, 20]:        )",
    "  #102= 1.",
    "N1000",
    "  IF [#102 GE 20.] GOTO 1002",
    "(     pass                      )",
    "  #102= #102 + 1.",
    "  GOTO 1000",
    "N1002",
)
def test_for2():
    x = Var()
    com("fish")
    for x in range(1, 20):
        pass


@must_be(
    "( x = Var[1, 2, 3, 4]           )",
    "  #100= 1.",
    "  #101= 2.",
    "  #102= 3.",
    "  #103= 4.",
    "( j = Var[0]                    )",
    "  #104= 0.",
    "( for v in x:                   )",
    "  #105= 100.",
    "N1000",
    "  IF [#105 GE 104.] GOTO 1002",
    "(     j += v                    )",
    "  #104= #104 + #[#105]",
    "  #105= #105 + 1.",
    "  GOTO 1000",
    "N1002",
)
def test_for4():
    x = Var(1, 2, 3, 4)
    j = Var(0)
    for v in x:
        j += v


@must_be(
    "Must be simple name as destination for 'for'.",
    "tests/test_for.py:10:17:18:     for v.var in x:",
    "                                                 ^",
)
def test_cerror_for5():
    x = Var(1, 2, 3, 4)
    j = Var(0)
    v = Var(0)
    for v.var in x:
        j += v


@must_be(
    "Illegal iterator.",
    "tests/test_for.py:7:20:21:     for x in [1, 2, 3]:",
    "                                                   ^",
)
def test_cerror_for11():
    for x in [1, 2, 3]:
        pass


@must_be(
    "Must be simple name as destination for 'for'.",
    "tests/test_for.py:7:25:26:     for V[0] in range(1, 9):",
    "                                                        ^",
)
def test_cerror_for():
    for V[0] in range(1, 9):
        pass
    else:
        V[1] = 10
