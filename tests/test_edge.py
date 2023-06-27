import p2g

from p2g.ptest import must_be


#! /usr/bin/env python

# make sure the testing is working.


@must_be(
    "( p2g.Fixed[2, addr=100]          )",
    "  #100= 2.                    ",
)
def test_ok2():
    z = p2g.Fixed[200](addr=123)
    p2g.Fixed(2, addr=100)


@must_be(
    "( zz[0] = 3                     )",
    "  #100= 3.                    ",
)
def test_ok():
    st = p2g.Table()

    zz = p2g.Var[200]()
    zz[0] = 3
