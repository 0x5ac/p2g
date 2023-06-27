from p2g import *
from p2g.ptest import must_be


TMP = Fixed[10](addr=400)


must_be(
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
    "( goto.feed[20].machine.xy_then_z[st.TMP2])",
    "  G01 G90 G53 F20. x'abc' y1.",
    "  G01 G90 G53 F20. z2.",
    "( goto.feed[20].machine.xy_then_z[st.TMP2.z])",
    "  G01 G90 G53 F20. x2.",
    "  G01 G90 G53 F20.",
)


def test_symtab():
    st = Table()
    comment("A")
    st.TMP = Fixed[10](addr=400)
    st.TMP.x = 9
    p = Const(78)
    q = Const(178)
    st.DINGO0 = Fixed(addr=100)
    st.DINGO1 = Var()
    st.DINGO2 = Const("a")

    st.DINGO0.x = st.DINGO0.x
    st.DINGO1.x = st.DINGO1.x
    st.DINGO1.x = st.DINGO2.x
    # st.DINGO1.var = st.DINGO2
    # st.DINGO2.var = st.DINGO0

    st.TMP1 = Var(p, p + q, 3, 4, 5, p, p + q)
    st.TMP2 = Const(
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
    goto.feed(20).machine.xy_then_z(st.TMP2)
    goto.feed(20).machine.xy_then_z(st.TMP2.z)
