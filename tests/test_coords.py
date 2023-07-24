from typing import Any

import p2g

from conftest import want


x = p2g.Fixed[10](addr=100)


class S:
    p: Any
    pass


# TESTS BELOW
@want(
    errors=[
        "Var can't have an address.                        ",
        "tests/test_coords.py:10:25:27:     v = p2g.Var[10](addr=20)",
        "                                                        ^^",
    ]
)
def test_cerror_addr0():
    # takes addr from specified.
    v = p2g.Var[10](addr=20)
    p2g.comment(v)


@want(
    errors=[
        "Conflicting sizes 100 and 1.                      ",
        "tests/test_coords.py:10:17:18:     p2g.Var[100](2)",
        "                                                ^ ",
    ]
)
def test_cerror_conflicting_sizes():
    #    with pytest.raises(SyntaxError, match="Conflicting sizes.*"):
    p2g.Var[100](2)


@want(
    errors=[
        "Const can't have an address.                      ",
        "tests/test_coords.py:10:28:31:     p2g.Const[2](1, 2, addr=123)",
        "                                                           ^^^",
    ]
)
def test_cerror_const1():
    #    with pytest.raises(SyntaxError, match="Const.*"):
    p2g.Const[2](1, 2, addr=123)


@want(
    errors=[
        "Overlapping axes [<2>] {'x': 3}.                  ",
        "tests/test_coords.py:10:17:18:     p2g.Var(2, x=3)",
        "                                                ^ ",
    ]
)
def test_cerror_overlapping():
    #    with pytest.raises(IndexError, match="Overlapping axes.*"):
    p2g.Var(2, x=3)


@want(
    errors=[
        "Conflicting sizes 10 and 4.                       ",
        "tests/test_coords.py:9:25:26:     p2g.Var[10](1, 2, 3, 4)",
        "                                                       ^",
    ]
)
def test_cerror_size0():
    p2g.Var[10](1, 2, 3, 4)


@want(
    errors=[
        "Const can't have an address.                      ",
        "tests/test_coords.py:9:22:23:     p2g.Const[2](addr=0)",
        "                                                    ^",
    ]
)
def test_cerror_zeros0():
    p2g.Const[2](addr=0)


@want(
    errors=[
        "Const can't have an address.                      ",
        "tests/test_coords.py:9:22:23:     p2g.Const[2](addr=0)",
        "                                                    ^",
    ]
)
def test_cerror_zeros1():
    p2g.Const[2](addr=0)


@want(
    errors=[
        "Conflicting sizes 0 and 3.                        ",
        "tests/test_coords.py:9:31:32:     p2g.Const[0](1, 2, 3, addr=0)",
        "                                                             ^",
    ]
)
def test_cerror_zeros2():
    p2g.Const[0](1, 2, 3, addr=0)


@want(
    errors=[
        "Zero sized vector.                                ",
        "tests/test_coords.py:9:14:15:     p2g.Const[0]()  ",
        "                                            ^     ",
    ]
)
def test_cerror_zeros3():
    p2g.Const[0]()


@want(
    "O00001 (test_kwargs)",
    "( Symbol Table )",
    "",
    " ( v :  #100.x  #101.y )",
    "",
    "( v = Var[x=2, y=3]             )",
    "  #100= 2.",
    "  #101= 3.",
    "",
    "( [array  100 2] )",
    "  M30",
    "%",
)
def test_kwargs():
    p2g.Control.symbol_table = True
    v = p2g.Var(x=2, y=3)
    p2g.comment(v)


@want(
    "O00001 (test_list_init0)",
    "( st.p = Fixed[[1, 2, 3, 4], addr=100])",
    "  #100= 1.",
    "  #101= 2.",
    "  #102= 3.",
    "  #103= 4.",
    "( st.p[1] = 3                   )",
    "  #101= 3.",
    "  M30",
    "%",
)
def test_list_init0():
    st = S()
    st.p = p2g.Fixed([1, 2, 3, 4], addr=100)
    st.p[1] = 3


@want(
    "O00001 (test_list_init1)",
    "( x[:] = [1, 2, 3]              )",
    "  #100= 1.",
    "  #101= 2.",
    "  #102= 3.",
    "  #103= 1.",
    "  #104= 2.",
    "  #105= 3.",
    "  #106= 1.",
    "  #107= 2.",
    "  #108= 3.",
    "  #109= 1.",
    "  M30",
    "%",
)
def test_list_init1():
    x[:] = [1, 2, 3]


@want(
    "O00001 (test_list_init2)",
    "( x[:-1] = [1, 2, 3]            )",
    "  #100= 1.",
    "  #101= 2.",
    "  #102= 3.",
    "  #103= 1.",
    "  #104= 2.",
    "  #105= 3.",
    "  #106= 1.",
    "  #107= 2.",
    "  #108= 3.",
    "  M30",
    "%",
)
def test_list_init2():
    x[:-1] = [1, 2, 3]


@want(
    "O00001 (test_list_init3)",
    "( x[3:-1] = [1, 2, 3]           )",
    "  #103= 1.",
    "  #104= 2.",
    "  #105= 3.",
    "  #106= 1.",
    "  #107= 2.",
    "  #108= 3.",
    "  M30",
    "%",
)
def test_list_init3():
    x[3:-1] = [1, 2, 3]


@want(
    "O00001 (test_non_kwargs)",
    "( v = Var[2, 3]                 )",
    "  #100= 2.",
    "  #101= 3.",
    "",
    "( [array  100 2] )",
    "  M30",
    "%",
)
def test_non_kwargs():
    v = p2g.Var(2, 3)
    p2g.comment(v)
