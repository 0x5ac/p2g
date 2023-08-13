import p2g

from conftest import want


# TESTS BELOW
########################################
@want(
    "O00001 (test_0)                                   ",
    "( Symbol Table )                                  ",
    "                                                  ",
    " ( flutes :  #200.x )                             ",
    " ( i      :  #100.x )                             ",
    " ( mx     :  #101.x )                             ",
    "                                                  ",
    "                                                  ",
    "( Yes this is a comment )                         ",
    "( mx = Var[flutes[0]]           )                 ",
    "  #101= #200                                      ",
    "( if i:                         )                 ",
    "  IF [#100 NE 0.] GOTO 1000                       ",
    "(     i += 9                    )                 ",
    "  #100= #100 + 9.                                 ",
    "  GOTO 1001                                       ",
    "N1000                                             ",
    "N1001                                             ",
    "( for i in flutes[1:]:          )                 ",
    "  #102= 201.                                      ",
    "N1002                                             ",
    "( for i in flutes[1:]:          )                 ",
    "  IF [#102 GE 210.] GOTO 1004                     ",
    "  #100= #[#102]                                   ",
    "(     if i > mx:                )                 ",
    "  IF [#100 LE #101] GOTO 1005                     ",
    "(         mx = i                )                 ",
    "  #101= #100                                      ",
    "  GOTO 1006                                       ",
    "N1005                                             ",
    "N1006                                             ",
    "(     assert i > 3              )                 ",
    "  IF [#100 LE 3.] 3001.= 100.                     ",
    "  #102= #102 + 1.                                 ",
    "  GOTO 1002                                       ",
    "N1004                                             ",
    "DPRNT[#100[42]]                                   ",
    "  M30                                             ",
    "%                                                 ",
)
def test_0():

    p2g.Control.symbol_table = True  #
    p2g.comment("Yes this is a comment")
    i = p2g.Var()
    flutes = p2g.Fixed[10](addr=200)
    mx = p2g.Var(flutes[0])
    if i:
        i += 9
    for i in flutes[1:]:
        if i > mx:
            mx = i
        assert i > 3
    p2g.sys.print(f"{i}")
