from typing import Any

import p2g

from conftest import want


class S:
    fish: Any
    EXTRALONGONEWITHEXTRA: Any
    PROBE_R: Any
    p: Any
    q: Any


class Q:
    def __init__(self):
        self.aaa1 = 999


FISH = p2g.Fixed(11111, 22222, 33333, 44444, 55555, addr=17)

T1 = p2g.Const(111111, 22222, 33333)
T3 = p2g.Const(111111, 22222, 33333)


# TESTS BELOW
@want(
    "O00001 (test_long_symtab)",
    "( FISH = Fixed[11111, 22222, 33333, 44444, 55555, addr=17])",
    "  #17= 11111.",
    "  #18= 22222.",
    "  #19= 33333.",
    "  #20= 44444.",
    "  #21= 55555.",
    "( Symbol Table )",
    "",
    " ( T1                                       : 111111.000,22222.000,...    )",
    " ( T3                                       : 111111.000,22222.000,...    )",
    " ( fish                                     :   1.000,  2.000,  3.000,... )",
    "",
    " ( FISH                                     :  #17[5]                     )",
    " ( XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX :  #100.x                     )",
    "",
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
    "  M30",
    "%",
)
def test_long_symtab():
    p2g.symbol.Table.print = True
    fish = p2g.Const(1, 2, 3, 4, 5, 6, 7)
    XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX = p2g.Var()
    p2g.Var(fish)
    XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX += 1


@want(
    "O00001 (test_symtab)",
    "( FISH = Fixed[11111, 22222, 33333, 44444, 55555, addr=17])",
    "  #17= 11111.",
    "  #18= 22222.",
    "  #19= 33333.",
    "  #20= 44444.",
    "  #21= 55555.",
    "( Symbol Table )",
    "",
    " ( T1                    : 111111.000,22222.000,... )",
    " ( T3                    : 111111.000,22222.000,... )",
    "",
    " ( EXTRALONGONEWITHEXTRA :  #100.x                  )",
    " ( FISH                  :  #17[5]                  )",
    " ( PROBE_R               :  #556.x                  )",
    " ( p                     :  #100.x                  )",
    "",
    "( p.x = 3                       )",
    "  #100= 3.",
    "( st.PROBE_R.x = 3              )",
    "  #556= 3.",
    "  M30",
    "%",
)
def test_symtab():
    p2g.symbol.Table.print = True
    st = S()
    st.EXTRALONGONEWITHEXTRA = p2g.Fixed[9](addr=100)
    p = p2g.Fixed[9](addr=100)
    st.fish = 3
    p.x = 3
    st.PROBE_R = p2g.Fixed[3](addr=556)
    st.PROBE_R.x = 3


@want(
    "O00001 (test_symtab1)",
    "( FISH = Fixed[11111, 22222, 33333, 44444, 55555, addr=17])",
    "  #17= 11111.",
    "  #18= 22222.",
    "  #19= 33333.",
    "  #20= 44444.",
    "  #21= 55555.",
    "( Symbol Table )",
    "",
    " ( T1   : 111111.000,22222.000,... )",
    " ( T3   : 111111.000,22222.000,... )",
    "",
    " ( FISH :  #17[5]                  )",
    " ( p    : #100[90]                 )",
    " ( q    :  #200.x  #202.z          )",
    "",
    "( p[17] = 31                    )",
    "  #117= 31.",
    "( p[18] = 123                   )",
    "  #118= 123.",
    "( st.q.x = 9                    )",
    "  #200= 9.",
    "( st.q.z = 91                   )",
    "  #202= 91.",
    "  M30",
    "%",
)
def test_symtab1():
    p2g.symbol.Table.print = True
    st = S()
    st.p = p2g.Fixed[90](addr=100)
    st.q = p2g.Fixed[3](addr=200)
    p = st.p
    # too far to get an axis name.
    p[17] = 31
    p[18] = 123
    st.q.x = 9
    st.q.z = 91


@want(
    "O00001 (test_symtab_long)",
    "( FISH = Fixed[11111, 22222, 33333, 44444, 55555, addr=17])",
    "  #17= 11111.",
    "  #18= 22222.",
    "  #19= 33333.",
    "  #20= 44444.",
    "  #21= 55555.",
    "( Symbol Table )",
    "",
    " ( T1    : 111111.000,22222.000,... )",
    " ( T3    : 111111.000,22222.000,... )",
    " ( pop   : 12345654321.000,...      )",
    "",
    " ( FISH  :  #17[5]                  )",
    " ( delta :  #17[5]                  )",
    " ( p1    :  #17[5]                  )",
    "",
    "( Var[q.aaa1]                   )",
    "  #100= 999.",
    "( Var[FISH]                     )",
    "  #101= #17",
    "  #102= #18",
    "  #103= #19",
    "  #104= #20",
    "  #105= #21",
    "( delta += delta + FISH         )",
    "  #17= #17 + #17 + #17",
    "  #18= #18 + #18 + #18",
    "  #19= #19 + #19 + #19",
    "  #20= #20 + #20 + #20",
    "  #21= #21 + #21 + #21",
    "( Var[delta]                    )",
    "  #106= #17",
    "  #107= #18",
    "  #108= #19",
    "  #109= #20",
    "  #110= #21",
    "( Var[pop]                      )",
    "  #111= 12345654321.",
    "  #112= 493817284.",
    "  #113= 1111088889.",
    "  M30",
    "%",
)
def test_symtab_long():
    class X:
        p1 = FISH

    q = Q()
    p2g.Var(q.aaa1)
    p2g.Var(FISH)
    delta = X.p1
    delta += delta + FISH
    pop = T1 * T3
    p2g.Var(delta)
    p2g.Var(pop)
    p2g.symbol.Table.print = True
