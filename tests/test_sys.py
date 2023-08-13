import p2g
from conftest import want

# TESTS BELOW
########################################
@want(
    "O00001 (test_bss)                                 ",
    "( x = Var[100]                  )                 ",
    "  #100= 100.                                      ",
    '(     sys.print[f"ABC {x+12}"]  )                 ',
    "  #101= #100 + 12.                                ",
    "DPRNT[ABC*#101[42]]                               ",
    "( y = Var[1000]                 )                 ",
    "  #101= 1000.                                     ",
    "                                                  ",
    "( Save bss at 102 )                               ",
    '(     sys.print[f"ABC {y+12}"]  )                 ',
    "  #102= #101 + 12.                                ",
    "DPRNT[ABC*#102[42]]                               ",
    "                                                  ",
    "( Restore bss to 102 )                            ",
    "  M30                                             ",
    "%                                                 ",
)
def test_bss():
    x = p2g.Var(100)
    with p2g.sys.BSS(quiet=True):
        p2g.sys.print(f"ABC {x+12}")

    y = p2g.Var(1000)
    with p2g.sys.BSS(quiet=False):
        p2g.sys.print(f"ABC {y+12}")


########################################
@want(
    "O00001 (test_ctx_off)                             ",
    "( with sys.Lookahead[False]:    )                 ",
    "  M97 P123                                        ",
    "(     goto[1, 2, 3]             )                 ",
    "  G90 G53 G01 G55 F8. x1. y2. z3.                 ",
    "  G103                                            ",
    "  M30                                             ",
    "N123                                              ",
    "  G103 P1                                         ",
    "  G04 P1                                          ",
    "  G04 P1                                          ",
    "  G04 P1                                          ",
    "  G04 P1                                          ",
    "  M99                                             ",
    "%                                                 ",
)
def test_ctx_off():
    goto = p2g.goto.feed(8).machine.all
    with p2g.sys.Lookahead(False):
        goto(1, 2, 3)


########################################
@want(
    "O00001 (test_ctx_on)                              ",
    "(     goto[1, 2, 3]             )                 ",
    "  G90 G53 G01 G55 F8. x1. y2. z3.                 ",
    "  M30                                             ",
    "%                                                 ",
)
def test_ctx_on():
    goto = p2g.goto.feed(8).machine.all
    with p2g.sys.Lookahead(True):
        goto(1, 2, 3)


########################################
@want(
    "O00001 (test_dangerous)                           ",
    "( sys.Lookahead.off[]           )                 ",
    "  M97 P123                                        ",
    "( goto[co]                      )                 ",
    "  G90 G53 G01 G55 F8. x1. y2. z3.                 ",
    "( sys.Lookahead.on[]            )                 ",
    "  G103                                            ",
    "( goto[co * 2]                  )                 ",
    "  G90 G53 G01 G55 F8. x2. y4. z6.                 ",
    "( sys.Lookahead.off[]           )                 ",
    "  M97 P123                                        ",
    "( goto[co * 3]                  )                 ",
    "  G90 G53 G01 G55 F8. x3. y6. z9.                 ",
    "  M30                                             ",
    "N123                                              ",
    "  G103 P1                                         ",
    "  G04 P1                                          ",
    "  G04 P1                                          ",
    "  G04 P1                                          ",
    "  G04 P1                                          ",
    "  M99                                             ",
    "%                                                 ",
)
def test_dangerous():
    goto = p2g.goto.feed(8).machine.all
    co = p2g.Const(1, 2, 3)
    p2g.sys.Lookahead.off()
    goto(co)
    p2g.sys.Lookahead.on()
    goto(co * 2)
    p2g.sys.Lookahead.off()
    goto(co * 3)


########################################
@want(
    "O00001 (test_off)                                 ",
    "( with sys.Lookahead[False]:    )                 ",
    "  M97 P123                                        ",
    "(     goto[1, 2, 3]             )                 ",
    "  G90 G53 G01 G55 F8. x1. y2. z3.                 ",
    "  G103                                            ",
    "  M30                                             ",
    "N123                                              ",
    "  G103 P1                                         ",
    "  G04 P1                                          ",
    "  G04 P1                                          ",
    "  G04 P1                                          ",
    "  G04 P1                                          ",
    "  M99                                             ",
    "%                                                 ",
)
def test_off():
    goto = p2g.goto.feed(8).machine.all
    with p2g.sys.Lookahead(False):
        goto(1, 2, 3)


########################################
@want(
    "O00001 (test_off_on)                              ",
    "( with sys.Lookahead[False]:    )                 ",
    "  M97 P123                                        ",
    "(     goto[1, 2, 3]             )                 ",
    "  G90 G53 G01 G55 F8. x1. y2. z3.                 ",
    "(     with sys.Lookahead[True]: )                 ",
    "  G103                                            ",
    "(         goto[1, 2, 3]         )                 ",
    "  G90 G53 G01 G55 F8. x1. y2. z3.                 ",
    "  M97 P123                                        ",
    "  G103                                            ",
    "  M30                                             ",
    "N123                                              ",
    "  G103 P1                                         ",
    "  G04 P1                                          ",
    "  G04 P1                                          ",
    "  G04 P1                                          ",
    "  G04 P1                                          ",
    "  M99                                             ",
    "%                                                 ",
)
def test_off_on():
    goto = p2g.goto.feed(8).machine.all
    with p2g.sys.Lookahead(False):
        goto(1, 2, 3)
        with p2g.sys.Lookahead(True):
            goto(1, 2, 3)


########################################
@want(
    "O00001 (test_on)                                  ",
    "(     goto[1, 2, 3]             )                 ",
    "  G90 G53 G01 G55 F8. x1. y2. z3.                 ",
    "  M30                                             ",
    "%                                                 ",
)
def test_on():
    goto = p2g.goto.feed(8).machine.all
    with p2g.sys.Lookahead(True):
        goto(1, 2, 3)


########################################
@want(
    "O00001 (test_on_off)                              ",
    "(     goto[1, 2, 3]             )                 ",
    "  G90 G53 G01 G55 F8. x1. y2. z3.                 ",
    "(     with sys.Lookahead[False]:)                 ",
    "  M97 P123                                        ",
    "(         goto[1, 2, 3]         )                 ",
    "  G90 G53 G01 G55 F8. x1. y2. z3.                 ",
    "  G103                                            ",
    "  M30                                             ",
    "N123                                              ",
    "  G103 P1                                         ",
    "  G04 P1                                          ",
    "  G04 P1                                          ",
    "  G04 P1                                          ",
    "  G04 P1                                          ",
    "  M99                                             ",
    "%                                                 ",
)
def test_on_off():
    goto = p2g.goto.feed(8).machine.all
    with p2g.sys.Lookahead(True):
        goto(1, 2, 3)
        with p2g.sys.Lookahead(False):
            goto(1, 2, 3)


########################################
@want(
    "O00001 (test_on_off_with_comment)                 ",
    "(     goto[1, 2, 3]             )                 ",
    "  G90 G53 G01 G55 F8. x1. y2. z3.                 ",
    "(     with sys.Lookahead[False]:)                 ",
    "  M97 P123                                        ",
    "(         goto[1, 2, 3]         )                 ",
    "  G90 G53 G01 G55 F8. x1. y2. z3.                 ",
    "  G103                                            ",
    "  M30                                             ",
    "N123                                              ",
    "  G103 P1                                         ",
    "  G04 P1                                          ",
    "  G04 P1                                          ",
    "  G04 P1                                          ",
    "  G04 P1                                          ",
    "  M99                                             ",
    "%                                                 ",
)
def test_on_off_with_comment():
    goto = p2g.goto.feed(8).machine.all
    with p2g.sys.Lookahead(True):
        goto(1, 2, 3)
        with p2g.sys.Lookahead(False):
            goto(1, 2, 3)
