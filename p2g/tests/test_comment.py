from p2g import *


@must_be_cc(
    "",
    "( a comment here )",
    "( Fixed[1, addr=100]            )",
    "  #100= 1.",
    "( no blank )",
    "  #100= 1.",
)
def test_comment0():
    # causes blank line before
    comment("a comment here")
    Fixed(1, addr=100)
    com("no blank")
    Fixed(1, addr=100)
