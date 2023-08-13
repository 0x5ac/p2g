import p2g

from conftest import want


# TESTS BELOW
########################################
@want(
    "O00001 (test_simple0)                             ",
    '( assert foo == "abc"           )                 ',
    "  ( ok )                                          ",
    "  M30                                             ",
    "%                                                 ",
)
def test_simple0():
    foo = "abc"
    assert foo == "abc"


########################################
@want(
    "O00001 (test_simple1)                             ",
    '( assert zap == "abcdef"        )                 ',
    "  ( ok )                                          ",
    "  M30                                             ",
    "%                                                 ",
)
def test_simple1():
    foo = "abc"
    bar = "def"
    zap = foo + bar
    assert zap == "abcdef"


########################################
@want(
    "O00001 (test_simple2)                             ",
    "( v1 = Var[len[zap]]            )                 ",
    "  #100= 6.                                        ",
    "( v2.var = v1.var               )                 ",
    "  #101= #100                                      ",
    "  M30                                             ",
    "%                                                 ",
)
def test_simple2():
    foo = "abc"
    bar = "def"
    zap = foo + bar
    v1 = p2g.Var(len(zap))
    v2 = p2g.Var()
    v2.var = v1.var


########################################
@want(
    "O00001 (test_simple3)                             ",
    "( v1 = Var[zap[0]]              )                 ",
    "  #100= 'a'                                       ",
    "( v2.var = v1.var               )                 ",
    "  #101= #100                                      ",
    "  M30                                             ",
    "%                                                 ",
)
def test_simple3():
    foo = "abc"
    bar = "def"
    zap = foo + bar
    v1 = p2g.Var(zap[0])
    v2 = p2g.Var()
    v2.var = v1.var


########################################
@want(
    "O00001 (test_simple4)                             ",
    '( v1["a"] = 9                   )                 ',
    "  #['a' + 100]= 9.                                ",
    "  M30                                             ",
    "%                                                 ",
)
def test_simple4():
    v1 = p2g.Var[10]()
    v1["a"] = 9


########################################
@want(
    "O00001 (test_simple_arrays)                       ",
    "( nw = Fixed[7][2, 2, 2, 2, 3, 3, 1, addr=200])   ",
    "  #200= 2.                                        ",
    "  #201= 2.                                        ",
    "  #202= 2.                                        ",
    "  #203= 2.                                        ",
    "  #204= 3.                                        ",
    "  #205= 3.                                        ",
    "  #206= 1.                                        ",
    "( nw[2] = 3                     )                 ",
    "  #202= 3.                                        ",
    "( nw[4] = 9                     )                 ",
    "  #204= 9.                                        ",
    "( idx = Fixed[7, addr=220]      )                 ",
    "  #220= 7.                                        ",
    "( fish.var = nw[idx // 1]       )                 ",
    "  #300= #[#220 + 200]                             ",
    "  M30                                             ",
    "%                                                 ",
)
def test_simple_arrays():
    nw = p2g.Fixed[7](2, 2, 2, 2, 3, 3, 1, addr=200)
    nw[2] = 3
    nw[4] = 9
    idx = p2g.Fixed(7, addr=220)
    fish = p2g.Fixed(addr=300)
    fish.var = nw[idx // 1]


########################################
@want(
    "O00001 (test_simple_code0)                        ",
    "( CURSOR = Var[20, 30]          )                 ",
    "  #300= 20.                                       ",
    "  #301= 30.                                       ",
    "( CURSOR.xy += [71, 17]         )                 ",
    "  #300= #300 + 71.                                ",
    "  #301= #301 + 17.                                ",
    "( CURSOR.y = haas.PROBE.y - 10  )                 ",
    "  #301= #5062 - 10.                               ",
    "( CURSOR.x = CURSOR.y           )                 ",
    "  #300= #301                                      ",
    "( CURSOR.y = 901                )                 ",
    "  #301= 901.                                      ",
    "( CURSOR[0:2] = haas.PROBE.xy * 2.0)              ",
    "  #300= #5061 * 2.                                ",
    "  #301= #5062 * 2.                                ",
    "  M30                                             ",
    "%                                                 ",
)
def test_simple_code0():
    p2g.sys.base_addr(300)

    CURSOR = p2g.Var(20, 30)
    #    CURSOR = [1, 7]
    CURSOR.xy += [71, 17]
    CURSOR.y = p2g.haas.PROBE.y - 10
    CURSOR.x = CURSOR.y

    CURSOR.y = 901
    CURSOR[0:2] = p2g.haas.PROBE.xy * 2.0
