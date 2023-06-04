#! /usr/bin/env python

import p2g


pop = 17


@p2g.must_be(
    "( q.xy = abs[t]     )",
    "  #100= 0.3333    ",
    "  #101= 0.6667",
)
def test_abs0():
    t = p2g.Const([-1 / 3.0, 2 / 3.0])
    q = p2g.Var[2]()
    q.xy = abs(t)


@p2g.must_be(
    "( q.xy = abs[q.xy]     )",
    "  #100= ABS#100      ",
    "  #101= ABS#101",
)
def test_abs1():
    t = p2g.Const([-1 / 3.0, 2 / 3.0])
    q = p2g.Var[2]()
    q.xy = abs(q.xy)


@p2g.must_be(
    "( pp.var = p2acos[p2cos[10.0]]  )",
    "  #100= 10.       ",
    "( pp.var = p2acos[p2cos[20.0]]  )",
    "  #100= 20.       ",
    "( pp.var = p2acos[p2cos[45.0]]  )",
    "  #100= 45.       ",
    "( pp.var = p2acos[p2cos[pp.var]])",
    "  #100= ACOS[COS[#100]]    ",
)
def test_cosacos():
    pp = p2g.Var()
    pp.var = p2g.acos(p2g.cos(10.0))
    pp.var = p2g.acos(p2g.cos(20.0))
    pp.var = p2g.acos(p2g.cos(45.0))
    pp.var = p2g.acos(p2g.cos(pp.var))


@p2g.must_be(
    "( pp.var = p2cos[10.0]    )",
    "  #100= 0.9848    ",
    "( pp.var = p2cos[20.0]    )",
    "  #100= 0.9397    ",
    "( pp.var = p2cos[45.0]    )",
    "  #100= 0.7071    ",
    "( pp.var = p2cos[pp.var]  )",
    "  #100= COS[#100]    ",
)
def test_cos():
    pp = p2g.Var()
    pp.var = p2g.cos(10.0)
    pp.var = p2g.cos(20.0)
    pp.var = p2g.cos(45.0)
    pp.var = p2g.cos(pp.var)


@p2g.must_be(
    "( pp.var = p2cos[pp.var]  )",
    "  #100= COS[#100]    ",
    "  #101= COS[#101]",
    "  #102= COS[#102]",
)
def test_cosx():
    #
    pp = p2g.Var[3]()
    pp.var = p2g.cos(pp.var)


@p2g.must_be(
    "( q.xy = p2exists[q.x]    )",
    "  #100= EXISTS[#100]    ",
    "  #101= EXISTS[#100]",
)
def test_exists():
    q = p2g.Var[2]()
    q.xy = p2g.exists(q.x)


@p2g.must_be(
    "( qq.var = p2fix[pp]   )",
    "  #106= FIX[#100]    ",
    "  #107= FIX[#101]",
    "  #108= FIX[#102]",
    "  #109= FIX[#103]",
    "  #110= FIX[#104]",
    "  #111= FIX[#105]",
    "( qq.var = p2fup[c1]   )",
    "  #106= -2.       ",
    "  #107= -1.",
    "  #108= 2.",
    "  #109= 2.",
    "  #110= -2.",
    "  #111= -1.",
    "( qq.var = p2fix[c1]   )",
    "  #106= -3.       ",
    "  #107= -2.",
    "  #108= 1.",
    "  #109= 1.",
    "  #110= -3.",
    "  #111= -2.",
    "( qq.var = p2ground[c1]   )",
    "  #106= -2.       ",
    "  #107= -2.",
    "  #108= 1.",
    "  #109= 2.",
    "  #110= -2.",
    "  #111= -2.",
    "( qq.var = p2fix[qq.xyz]  )",
    "  #106= FIX[#106]    ",
    "  #107= FIX[#107]",
    "  #108= FIX[#108]",
    "  #109= FIX[#106]",
    "  #110= FIX[#107]",
    "  #111= FIX[#108]",
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


@p2g.must_be(
    "( pp.var = p2ln[p2exp[1.23]] )",
    "  #100= 1.23      ",
    "( pp.var = p2exp[p2ln[1.23]] )",
    "  #100= 1.23      ",
    "( pp.var = p2exp[pp.var]  )",
    "  #100= EXP[#100]    ",
    "( pp.var = p2ln[pp.var]   )",
    "  #100= LN[#100]     ",
)
def test_lnexp():
    pp = p2g.Var()
    pp.var = p2g.ln(p2g.exp(1.23))
    pp.var = p2g.exp(p2g.ln(1.23))
    pp.var = p2g.exp(pp.var)
    pp.var = p2g.ln(pp.var)


@p2g.must_be(
    "( q.xy = round[t, 2]   )",
    "  #100= 0.33      ",
    "  #101= 0.67",
)
def test_round():
    t = p2g.Const([1 / 3.0, 2 / 3.0])
    q = p2g.Var[2]()
    q.xy = round(t, 2)


@p2g.must_be(
    "( pp.var = p2asin[p2sin[10.0]]  )",
    "  #100= 10.       ",
    "( pp.var = p2asin[p2sin[20.0]]  )",
    "  #100= 20.       ",
    "( pp.var = p2asin[p2sin[45.0]]  )",
    "  #100= 45.       ",
    "( pp.var = p2asin[p2sin[pp.var]])",
    "  #100= ASIN[SIN[#100]]    ",
)
def test_sinasin():
    pp = p2g.Var()
    pp.var = p2g.asin(p2g.sin(10.0))
    pp.var = p2g.asin(p2g.sin(20.0))
    pp.var = p2g.asin(p2g.sin(45.0))
    pp.var = p2g.asin(p2g.sin(pp.var))


@p2g.must_be(
    "( pp.var = p2sin[10.0]    )",
    "  #100= 0.1736    ",
    "( pp.var = p2sin[20.0]    )",
    "  #100= 0.342     ",
    "( pp.var = p2sin[45.0]    )",
    "  #100= 0.7071    ",
    "( pp.var = p2sin[pp.var]  )",
    "  #100= SIN[#100]    ",
)
def test_sin():
    pp = p2g.Var()
    pp.var = p2g.sin(10.0)
    pp.var = p2g.sin(20.0)
    pp.var = p2g.sin(45.0)
    pp.var = p2g.sin(pp.var)


@p2g.must_be(
    "( qq.var = p2fix[pp]   )",
    "  #106= FIX[#100]    ",
    "  #107= FIX[#101]",
    "  #108= FIX[#102]",
    "  #109= FIX[#103]",
    "  #110= FIX[#104]",
    "  #111= FIX[#105]",
    "( qq.var = p2sqrt[c1] * p2sqrt[c1])",
    "  #106= 0.1       ",
    "  #107= 1.6",
    "  #108= 1.2",
    "  #109= 1.7",
    "  #110= 0.1",
    "  #111= 1.6",
    "( qq.var = p2sqrt[qq.xyz] * 3   )",
    "  #106= SQRT[#106] * 3.    ",
    "  #107= SQRT[#107] * 3.",
    "  #108= SQRT[#108] * 3.",
    "  #109= SQRT[#106] * 3.",
    "  #110= SQRT[#107] * 3.",
    "  #111= SQRT[#108] * 3.",
)
def test_sqrt():
    pp = p2g.Var[6]()
    qq = p2g.Var[6]()
    qq.var = p2g.fix(pp)
    c1 = p2g.Const([0.1, 1.6, 1.2, 1.7])
    qq.var = p2g.sqrt(c1) * p2g.sqrt(c1)
    qq.var = p2g.sqrt(qq.xyz) * 3


@p2g.must_be(
    "( pp.var = p2atan[p2tan[10.0]]  )",
    "  #100= 10.       ",
    "( pp.var = p2atan[p2tan[20.0]]  )",
    "  #100= 20.       ",
    "( pp.var = p2atan[p2tan[45.0]]  )",
    "  #100= 45.       ",
    "( pp.var = p2atan[p2tan[pp.var]])",
    "  #100= ATAN[TAN[#100]]    ",
)
def test_tanatan():
    pp = p2g.Var()
    pp.var = p2g.atan(p2g.tan(10.0))
    pp.var = p2g.atan(p2g.tan(20.0))
    pp.var = p2g.atan(p2g.tan(45.0))
    pp.var = p2g.atan(p2g.tan(pp.var))


@p2g.must_be(
    "( pp.var = p2tan[10.0]    )",
    "  #100= 0.1763    ",
    "( pp.var = p2tan[20.0]    )",
    "  #100= 0.364     ",
    "( pp.var = p2tan[45.0]    )",
    "  #100= 1.     ",
    "( pp.var = p2tan[pp.var]  )",
    "  #100= TAN[#100]    ",
)
def test_tan():
    pp = p2g.Var()
    pp.var = p2g.tan(10.0)
    pp.var = p2g.tan(20.0)
    pp.var = p2g.tan(45.0)
    pp.var = p2g.tan(pp.var)
