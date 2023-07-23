from typing import Any

import p2g

from conftest import want


class ITable:
    TMP: Any
    TMP1: Any
    TMP2: Any
    DINGO0: p2g.CoType
    DINGO1: p2g.CoType
    DINGO2: p2g.CoType


TMP = p2g.Fixed[10](addr=400)

# TESTS BELOW


@want(
    "O00001 (test_symtab)",
    "",
    "( A )",
    "( st.TMP.x = 9                  )",
    "  #400= 9.",
    "( st.DINGO1.x = st.DINGO2.x     )",
    "  #100= 97.",
    "( st.TMP1 = Var[p, p + q, 3, 4, 5, p, p + q])",
    "  #101= 78.",
    "  #102= 256.",
    "  #103= 3.",
    "  #104= 4.",
    "  #105= 5.",
    "  #106= 78.",
    "  #107= 256.",
    "( goto.feed[20].machine.z_last[st.TMP2])",
    "  G90 G53 G01 G55 F20. x'abc' y1.",
    "  G90 G53 G01 G55 F20. z2.",
    "( goto.feed[20].machine.z_last[st.TMP2.z])",
    "  G90 G53 G01 G55 F20. x2.",
    "  M30",
    "%",
)
def test_symtab():
    st = ITable()
    p2g.comment("A")
    st.TMP = p2g.Fixed[10](addr=400)
    st.TMP.x = 9
    p = p2g.Const(78)
    q = p2g.Const(178)
    st.DINGO0 = p2g.Fixed(addr=100)
    st.DINGO1 = p2g.Var()
    st.DINGO2 = p2g.Const("a")

    st.DINGO0.x = st.DINGO0.x
    st.DINGO1.x = st.DINGO1.x
    st.DINGO1.x = st.DINGO2.x
    # st.DINGO1.var = st.DINGO2
    # st.DINGO2.var = st.DINGO0

    st.TMP1 = p2g.Var(p, p + q, 3, 4, 5, p, p + q)
    st.TMP2 = p2g.Const(
        "abc",
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
    )
    p2g.goto.feed(20).machine.z_last(st.TMP2)
    p2g.goto.feed(20).machine.z_last(st.TMP2.z)
