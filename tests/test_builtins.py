import p2g

from conftest import want


pop = 17
# TESTS BELOW
########################################
@want(
    "O00001 (test_abs0)                                ",
    "( q.xy = abs[t]                 )                 ",
    "  #100= 0.3333                                    ",
    "  #101= 0.6667                                    ",
    "  M30                                             ",
    "%                                                 ",
)
def test_abs0():
    t = p2g.Const([-1 / 3.0, 2 / 3.0])
    q = p2g.Var[2]()
    q.xy = abs(t)


########################################
@want(
    "O00001 (test_abs1)                                ",
    "( q.xy = abs[q.xy]              )                 ",
    "  #100= ABS#100                                   ",
    "  #101= ABS#101                                   ",
    "  M30                                             ",
    "%                                                 ",
)
def test_abs1():
    p2g.Const([-1 / 3.0, 2 / 3.0])
    q = p2g.Var[2]()
    q.xy = abs(q.xy)


########################################
@want(
    "O00001 (test_cos)                                 ",
    "( pp.var = cos[10.0]            )                 ",
    "  #100= 0.9848                                    ",
    "( pp.var = cos[20.0]            )                 ",
    "  #100= 0.9397                                    ",
    "( pp.var = cos[45.0]            )                 ",
    "  #100= 0.7071                                    ",
    "( pp.var = cos[pp.var]          )                 ",
    "  #100= COS[#100]                                 ",
    "  M30                                             ",
    "%                                                 ",
)
def test_cos():
    pp = p2g.Var()
    pp.var = p2g.cos(10.0)
    pp.var = p2g.cos(20.0)
    pp.var = p2g.cos(45.0)
    pp.var = p2g.cos(pp.var)


########################################
@want(
    "O00001 (test_cosacos)                             ",
    "( pp.var = acos[cos[10.0]]      )                 ",
    "  #100= 10.                                       ",
    "( pp.var = acos[cos[20.0]]      )                 ",
    "  #100= 20.                                       ",
    "( pp.var = acos[cos[45.0]]      )                 ",
    "  #100= 45.                                       ",
    "( pp.var = acos[cos[pp.var]]    )                 ",
    "  #100= ACOS[COS[#100]]                           ",
    "  M30                                             ",
    "%                                                 ",
)
def test_cosacos():
    pp = p2g.Var()
    pp.var = p2g.acos(p2g.cos(10.0))
    pp.var = p2g.acos(p2g.cos(20.0))
    pp.var = p2g.acos(p2g.cos(45.0))
    pp.var = p2g.acos(p2g.cos(pp.var))


########################################
@want(
    "O00001 (test_cosx)                                ",
    "( pp.var = cos[pp.var]          )                 ",
    "  #100= COS[#100]                                 ",
    "  #101= COS[#101]                                 ",
    "  #102= COS[#102]                                 ",
    "  M30                                             ",
    "%                                                 ",
)
def test_cosx():
    #
    pp = p2g.Var[3]()
    pp.var = p2g.cos(pp.var)


########################################
@want(
    "O00001 (test_exists)                              ",
    "( q.xy = exists[q.x]            )                 ",
    "  #100= EXISTS[#100]                              ",
    "  #101= EXISTS[#100]                              ",
    "  M30                                             ",
    "%                                                 ",
)
def test_exists():
    q = p2g.Var[2]()
    q.xy = p2g.exists(q.x)


########################################
@want(
    "O00001 (test_fixfup)                              ",
    "( qq.var = fix[pp]              )                 ",
    "  #106= FIX[#100]                                 ",
    "  #107= FIX[#101]                                 ",
    "  #108= FIX[#102]                                 ",
    "  #109= FIX[#103]                                 ",
    "  #110= FIX[#104]                                 ",
    "  #111= FIX[#105]                                 ",
    "( qq.var = fup[c1]              )                 ",
    "  #106= -2.                                       ",
    "  #107= -1.                                       ",
    "  #108= 2.                                        ",
    "  #109= 2.                                        ",
    "  #110= -2.                                       ",
    "  #111= -1.                                       ",
    "( qq.var = fix[c1]              )                 ",
    "  #106= -3.                                       ",
    "  #107= -2.                                       ",
    "  #108= 1.                                        ",
    "  #109= 1.                                        ",
    "  #110= -3.                                       ",
    "  #111= -2.                                       ",
    "( qq.var = ground[c1]           )                 ",
    "  #106= -2.                                       ",
    "  #107= -2.                                       ",
    "  #108= 1.                                        ",
    "  #109= 2.                                        ",
    "  #110= -2.                                       ",
    "  #111= -2.                                       ",
    "( qq.var = fix[qq.xyz]          )                 ",
    "  #106= FIX[#106]                                 ",
    "  #107= FIX[#107]                                 ",
    "  #108= FIX[#108]                                 ",
    "  #109= FIX[#106]                                 ",
    "  #110= FIX[#107]                                 ",
    "  #111= FIX[#108]                                 ",
    "  M30                                             ",
    "%                                                 ",
)
def test_fixfup():
    pp = p2g.Var[6]()
    qq = p2g.Var[6]()
    qq.var = p2g.fix(pp)
    c1 = p2g.Const([-2.1, -1.6, 1.2, 1.7])
    qq.var = p2g.fup(c1)
    qq.var = p2g.fix(c1)
    qq.var = p2g.ground(c1)
    qq.var = p2g.fix(qq.xyz)


########################################
@want(
    "O00001 (test_lnexp)                               ",
    "( pp.var = ln[exp[1.23]]        )                 ",
    "  #100= 1.23                                      ",
    "( pp.var = exp[ln[1.23]]        )                 ",
    "  #100= 1.23                                      ",
    "( pp.var = exp[pp.var]          )                 ",
    "  #100= EXP[#100]                                 ",
    "( pp.var = ln[pp.var]           )                 ",
    "  #100= LN[#100]                                  ",
    "  M30                                             ",
    "%                                                 ",
)
def test_lnexp():
    pp = p2g.Var()
    pp.var = p2g.ln(p2g.exp(1.23))
    pp.var = p2g.exp(p2g.ln(1.23))
    pp.var = p2g.exp(pp.var)
    pp.var = p2g.ln(pp.var)


########################################
@want(
    "O00001 (test_round)                               ",
    "( q.xy = round[t, 2]            )                 ",
    "  #100= 0.33                                      ",
    "  #101= 0.67                                      ",
    "  M30                                             ",
    "%                                                 ",
)
def test_round():
    t = p2g.Const([1 / 3.0, 2 / 3.0])
    q = p2g.Var[2]()
    q.xy = round(t, 2)


########################################
@want(
    "O00001 (test_sin)                                 ",
    "( pp.var = sin[10.0]            )                 ",
    "  #100= 0.1736                                    ",
    "( pp.var = sin[20.0]            )                 ",
    "  #100= 0.342                                     ",
    "( pp.var = sin[45.0]            )                 ",
    "  #100= 0.7071                                    ",
    "( pp.var = sin[pp.var]          )                 ",
    "  #100= SIN[#100]                                 ",
    "  M30                                             ",
    "%                                                 ",
)
def test_sin():
    pp = p2g.Var()
    pp.var = p2g.sin(10.0)
    pp.var = p2g.sin(20.0)
    pp.var = p2g.sin(45.0)
    pp.var = p2g.sin(pp.var)


########################################
@want(
    "O00001 (test_sinasin)                             ",
    "( pp.var = asin[sin[10.0]]      )                 ",
    "  #100= 10.                                       ",
    "( pp.var = asin[sin[20.0]]      )                 ",
    "  #100= 20.                                       ",
    "( pp.var = asin[sin[45.0]]      )                 ",
    "  #100= 45.                                       ",
    "( pp.var = asin[sin[pp.var]]    )                 ",
    "  #100= ASIN[SIN[#100]]                           ",
    "  M30                                             ",
    "%                                                 ",
)
def test_sinasin():
    pp = p2g.Var()
    pp.var = p2g.asin(p2g.sin(10.0))
    pp.var = p2g.asin(p2g.sin(20.0))
    pp.var = p2g.asin(p2g.sin(45.0))
    pp.var = p2g.asin(p2g.sin(pp.var))


########################################
@want(
    "O00001 (test_sqrt)                                ",
    "( qq.var = fix[pp]              )                 ",
    "  #106= FIX[#100]                                 ",
    "  #107= FIX[#101]                                 ",
    "  #108= FIX[#102]                                 ",
    "  #109= FIX[#103]                                 ",
    "  #110= FIX[#104]                                 ",
    "  #111= FIX[#105]                                 ",
    "( qq.var = sqrt[c1] * sqrt[c1]  # type: ignore)   ",
    "  #106= 0.1                                       ",
    "  #107= 1.6                                       ",
    "  #108= 1.2                                       ",
    "  #109= 1.7                                       ",
    "  #110= 0.1                                       ",
    "  #111= 1.6                                       ",
    "( qq.var = sqrt[qq.xyz] * 3  # type: ignore)      ",
    "  #106= SQRT[#106] * 3.                           ",
    "  #107= SQRT[#107] * 3.                           ",
    "  #108= SQRT[#108] * 3.                           ",
    "  #109= SQRT[#106] * 3.                           ",
    "  #110= SQRT[#107] * 3.                           ",
    "  #111= SQRT[#108] * 3.                           ",
    "  M30                                             ",
    "%                                                 ",
)
def test_sqrt():
    pp = p2g.Var[6]()
    qq = p2g.Var[6]()
    qq.var = p2g.fix(pp)
    c1 = p2g.Const([0.1, 1.6, 1.2, 1.7])
    qq.var = p2g.sqrt(c1) * p2g.sqrt(c1)  # type: ignore
    qq.var = p2g.sqrt(qq.xyz) * 3  # type: ignore


########################################
@want(
    "O00001 (test_tan)                                 ",
    "( pp.var = tan[10.0]            )                 ",
    "  #100= 0.1763                                    ",
    "( pp.var = tan[20.0]            )                 ",
    "  #100= 0.364                                     ",
    "( pp.var = tan[45.0]            )                 ",
    "  #100= 1.                                        ",
    "( pp.var = tan[pp.var]          )                 ",
    "  #100= TAN[#100]                                 ",
    "  M30                                             ",
    "%                                                 ",
)
def test_tan():
    pp = p2g.Var()
    pp.var = p2g.tan(10.0)
    pp.var = p2g.tan(20.0)
    pp.var = p2g.tan(45.0)
    pp.var = p2g.tan(pp.var)


########################################
@want(
    "O00001 (test_tanatan)                             ",
    "( pp.var = atan[tan[10.0]]      )                 ",
    "  #100= 10.                                       ",
    "( pp.var = atan[tan[20.0]]      )                 ",
    "  #100= 20.                                       ",
    "( pp.var = atan[tan[45.0]]      )                 ",
    "  #100= 45.                                       ",
    "( pp.var = atan[tan[pp.var]]    )                 ",
    "  #100= ATAN[TAN[#100]]                           ",
    "  M30                                             ",
    "%                                                 ",
)
def test_tanatan():
    pp = p2g.Var()
    pp.var = p2g.atan(p2g.tan(10.0))
    pp.var = p2g.atan(p2g.tan(20.0))
    pp.var = p2g.atan(p2g.tan(45.0))
    pp.var = p2g.atan(p2g.tan(pp.var))
