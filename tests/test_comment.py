import p2g


@p2g.ptest.must_be_cc(
    "",
    "( a comment here )",
    "( Fixed[1, addr=100]            )",
    "  #100= 1.",
    "( no blank )",
    "  #100= 1.",
)
def test_comment0():
    # causes blank line before
    p2g.comment("a comment here")
    p2g.Fixed(1, addr=100)
    p2g.com("no blank")
    p2g.Fixed(1, addr=100)
