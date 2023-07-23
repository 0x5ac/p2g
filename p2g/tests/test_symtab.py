import p2g


class S:
    pass


@p2g.must_be_cc(
    "( XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX :  #100.x                     )",
    "( fish                                     :   1.000,  2.000,  3.000,... )",
    "( Var[fish]                     )",
    "  #101= 1.",
    "  #102= 2.",
    "  #103= 3.",
    "  #104= 4.",
    "  #105= 5.",
    "  #106= 6.",
    "  #107= 7.",
    "( XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX += 1)",
    "  #100= #100 + 1.",
)
def test_long_symtab():
    p2g.symbol.Table.print = 1
    fish = p2g.Const(1, 2, 3, 4, 5, 6, 7)
    XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX = p2g.Var()
    p2g.Var(fish)
    XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX += 1


@p2g.must_be_cc(
    "( p       :  #100.x )",
    "( PROBE_R :  #556.x )",
    "( p.x = 3                       )",
    "  #100= 3.",
    "( st.PROBE_R.x = 3              )",
    "  #556= 3.",
)
def test_symtab():
    p2g.symbol.Table.print = 1
    st = S()
    st.EXTRALONGONEWITHEXTRA = p2g.Fixed[9](addr=100)
    p = p2g.Fixed[9](addr=100)
    st.fish = 3
    p.x = 3
    st.PROBE_R = p2g.Fixed[3](addr=556)
    st.PROBE_R.x = 3


@p2g.must_be_cc(
    "( p : #100[90]        )",
    "( q :  #200.x  #202.z )",
    "( p[17] = 31                    )",
    "  #117= 31.",
    "( p[18] = 123                   )",
    "  #118= 123.",
    "( st.q.x = 9                    )",
    "  #200= 9.",
    "( st.q.z = 91                   )",
    "  #202= 91.",
)
def test_symtab1():
    p2g.symbol.Table.print = 1
    st = S()
    st.p = p2g.Fixed[90](addr=100)
    st.q = p2g.Fixed[3](addr=200)
    p = st.p
    # too far to get an axis name.
    p[17] = 31
    p[18] = 123
    st.q.x = 9
    st.q.z = 91
