import p2g

from conftest import want


# TESTS BELOW
########################################
@want(
    "O00001 (test_comment0)                            ",
    "                                                  ",
    "( a comment here )                                ",
    "  #100= 1.                        ( Fixed[1, addr=100]            )",
    "( no blank )                                      ",
    "  #100= 1.                                        ",
    "  M30                                             ",
    "%                                                 ",
    narrow_output=False,
)
def test_comment0():
    # causes blank line before
    p2g.comment("a comment here")
    p2g.Fixed(1, addr=100)
    p2g.com("no blank")
    p2g.Fixed(1, addr=100)


########################################
@want(
    "O00001 (test_narrow_output_comment)               ",
    "                                                  ",
    "( LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL )",
    "  #100= 7.                        ( Var[7]                        )",
    "  M30                                             ",
    "%                                                 ",
    narrow_output=False,
)
def test_narrow_output_comment():
    p2g.comment("LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL")
    p2g.Var(7)


########################################
@want(
    "O00001 (test_wide_output_comment)                 ",
    "                                                  ",
    "( LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL )",
    "  #100= 7.                        ( Var[7]                        )",
    "  M30                                             ",
    "%                                                 ",
    narrow_output=False,
)
def test_wide_output_comment():
    p2g.comment("LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL")
    p2g.Var(7)
