#! /usr/bin/env python

# make sure the testing is working.

import p2g


@p2g.must_be(
    "( p2g.Fixed[2, addr=100]          )",
    "  #100= 2.                    ",
)
def test_ok2():
    z = p2g.Fixed[200](addr=123)
    p2g.Fixed(2, addr=100)


@p2g.must_be(
    "( zz[0] = 3                     )",
    "  #100= 3.                    ",
)
def test_ok():
    st = p2g.Symbols()

    zz = p2g.Var[200]()
    zz[0] = 3
    st.insert_symbol_table()
