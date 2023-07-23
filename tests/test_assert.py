import p2g

from conftest import want


# TESTS BELOW
@want(
    "O00001 (test_assert1)",
    '( assert 1, "NEVER OUTPUT"      )',
    "  ( ok )",
    "  M30",
    "%",
)
def test_assert1():
    assert 1, "NEVER OUTPUT"


@want(
    "O00001 (test_assert2)",
    '( assert 0, "ALWAYS OUTPUT"     )',
    "  3001.= 100. ( ALWAYS OUTPUT )",
    "  M30",
    "%",
)
def test_assert2():
    assert 0, "ALWAYS OUTPUT"


@want(
    "O00001 (test_assert3)",
    "( assert 0                      )",
    "  3001.= 100.",
    "  M30",
    "%",
)
def test_assert3():
    assert 0


@want(
    "O00001 (test_assert4)",
    "( assert 1                      )",
    "  ( ok )",
    "  M30",
    "%",
)
def test_assert4():
    assert 1


@want(
    "O00001 (test_assert5)",
    '( assert x == 3, "CONDITIONAL"  )',
    "  IF [#100 NE 3.] 3001.= 100. ( CONDITIONAL )",
    "  M30",
    "%",
)
def test_assert5():
    x = p2g.Var()
    assert x == 3, "CONDITIONAL"


@want(
    "O00001 (test_assert6)",
    "( assert x == 9                 )",
    "  IF [#100 NE 9.] 3001.= 100.",
    "  M30",
    "%",
)
def test_assert6():
    x = p2g.Var()
    assert x == 9
