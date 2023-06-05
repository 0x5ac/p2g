from p2g import *


@must_be_cc(
    "( a comment here )",
    "( Fixed[1, addr=100]            )",
    "  #100= 1.",
)
def test_comment0():
    comment("a comment here")
    Fixed(1, addr=100)
