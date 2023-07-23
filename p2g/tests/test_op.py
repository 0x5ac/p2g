import p2g


@p2g.must_be(
    "( a.var += 17                   )",
    "  #1= #1 + 17.                ",
    "( a.var &= 17                   )",
    "  #1= #1 AND 17.              ",
    "( a.var |= 17                   )",
    "  #1= #1 OR 17.               ",
    "( a.var -= 17                   )",
    "  #1= #1 - 17.                ",
    "( a.var *= 17                   )",
    "  #1= #1 * 17.                ",
    "( a.var /= 17                   )",
    "  #1= #1 / 17.                ",
    "( a.var //= 17                  )",
    "  #1= #1 // 17.               ",
    "( a.var %= 17                   )",
    "  #1= #1 MOD 17.              ",
)
def test_augass0():
    a = p2g.Fixed(addr=1)
    a.var += 17
    a.var &= 17
    a.var |= 17
    a.var -= 17
    a.var *= 17
    a.var /= 17
    a.var //= 17
    a.var %= 17


@p2g.must_be(
    "( T.var = not 1                 )",
    "  #100= 0.                    ",
    "( T.var = not [not 1]           )",
    "  #100= 1.                    ",
    "( T.var = not [not [not 1]]     )",
    "  #100= 0.                    ",
    "( T.var = not T                 )",
    "  #100= #100 NE 0.            ",
    "( T.var = not [not T]           )",
    "  #100= #100 EQ 0.            ",
    "( T.var = not [not [not T]]     )",
    "  #100= #100 NE 0.            ",
    "( T.var = T.var > 9             )",
    "  #100= #100 GT 9.            ",
    "( T.var = not [T.var > 9]       )",
    "  #100= #100 LE 9.            ",
    "( T.var = not [not [T.var > 9]] )",
    "  #100= #100 GT 9.            ",
    "( T.var = not [[T.var > 9] != 0])",
    "  #100= #100 LE 9.            ",
    "( T.var = not [not [[T.var > 9] != 0]])",
    "  #100= #100 GT 9.            ",
    "( T.var = not [not [[T.var > 9] != 0]] == 0)",
    "  #100= #100 LE 9.            ",
    "( T.var = 99999                 )",
    "  #100= 99999.                ",
    "( T.var = T == 9                )",
    "  #100= #100 EQ 9.            ",
    "( T.var = [T == 9] == 0         )",
    "  #100= #100 NE 9.            ",
    "( T.var = [[T == 9] == 0] == 0  )",
    "  #100= #100 EQ 9.            ",
    "( T.var = [[[T == 9] == 0] == 0] == 0)",
    "  #100= #100 NE 9.            ",
    "( T.var = 88888                 )",
    "  #100= 88888.                ",
    "( T.var = T != 9                )",
    "  #100= #100 NE 9.            ",
    "( T.var = [T == 9] == 0         )",
    "  #100= #100 NE 9.            ",
    "( T.var = [T == 9] != 0         )",
    "  #100= #100 EQ 9.            ",
    "( T.var = [[T == 9] == 0] == 0  )",
    "  #100= #100 EQ 9.            ",
    "( T.var = [[T == 9] != 0] != 0  )",
    "  #100= #100 EQ 9.            ",
    "( T.var = [[T == 9] == 0] != 0  )",
    "  #100= #100 NE 9.            ",
    "( T.var = [[T == 9] != 0] == 0  )",
    "  #100= #100 NE 9.            ",
    "( T.var = 9                     )",
    "  #100= 9.                    ",
    "( T.var = T == 9                )",
    "  #100= #100 EQ 9.            ",
    "( T.var = T != 9                )",
    "  #100= #100 NE 9.            ",
    "( T.var = not [T == 9]          )",
    "  #100= #100 NE 9.            ",
    "( T.var = not [T == 9] != 0     )",
    "  #100= #100 NE 9.            ",
    "( T.var = not [[T == 9] == 0] == 0)",
    "  #100= #100 NE 9.            ",
    "( T.var = not [[T == 9] != 0] != 0)",
    "  #100= #100 NE 9.            ",
    "( T.var = not [[T == 9] == 0] != 0)",
    "  #100= #100 EQ 9.            ",
    "( T.var = not [[T == 9] != 0] == 0)",
    "  #100= #100 EQ 9.            ",
)
def test_basic_folding0():
    T = p2g.Var()
    T.var = not 1
    T.var = not (not 1)
    T.var = not (not (not 1))
    T.var = T
    T.var = not T
    T.var = not (not T)
    T.var = not (not (not T))
    T.var = T.var > 9
    T.var = not (T.var > 9)
    T.var = not (not (T.var > 9))
    T.var = not ((T.var > 9) != 0)
    T.var = not (not ((T.var > 9) != 0))
    T.var = not (not ((T.var > 9) != 0)) == 0
    T.var = 99999
    T.var = T == 9
    T.var = (T == 9) == 0
    T.var = ((T == 9) == 0) == 0
    T.var = (((T == 9) == 0) == 0) == 0
    T.var = 88888
    T.var = T != 9

    T.var = (T == 9) == 0
    T.var = (T == 9) != 0
    T.var = ((T == 9) == 0) == 0
    T.var = ((T == 9) != 0) != 0
    T.var = ((T == 9) == 0) != 0
    T.var = ((T == 9) != 0) == 0

    T.var = 9
    T.var = T == 9
    T.var = T != 9
    T.var = not (T == 9)
    T.var = not (T == 9) != 0
    T.var = not ((T == 9) == 0) == 0
    T.var = not ((T == 9) != 0) != 0
    T.var = not ((T == 9) == 0) != 0
    T.var = not ((T == 9) != 0) == 0


@p2g.must_be(
    "( T.var = T - 10 - 11           )",
    "  #100= #100 - 21.            ",
    "( T.var = T - [-X]              )",
    "  #100= #100 + #101           ",
    "( T.var = T * -1.0              )",
    "  #100= -#100                 ",
    "( T.var = T * 0.0               )",
    "  #100= 0.                    ",
    "( P = p2Var[2][17, 20]          )",
    "  #102= 17.                   ",
    "  #103= 20.",
    "( P.var *= V                    )",
    "  #102= -#102                 ",
    "( P.var += V - U                )",
    "  #102= #102 - 2.             ",
    "  #103= #103 + 2.",
    "( Q.xy += [103, 203]            )",
    "  #177= #177 + 103.           ",
    "  #178= #178 + 203.",
    "( Q.xy += p2ConstVec[[103, 203]] * 7)",
    "  #177= #177 + 721.           ",
    "  #178= #178 + 1421.",
)
def test_basic_folding1():
    T = p2g.Var()
    X = p2g.Var()
    T.var = T - 10 - 11
    T.var = T - (-X)
    T.var = T * -1.0
    T.var = T * 1.0
    T.var = T * 0.0

    V = p2g.Const[2](-1, 1)
    U = p2g.Const[2](1, -1)
    P = p2g.Var[2](17, 20)
    Q = p2g.Fixed[2](addr=177)

    P.var *= V
    P.var += V - U
    Q.xy += [103, 203]
    Q.xy += p2g.RValueVec([103, 203]) * 7


@p2g.must_be(
    "( a.var &= 123123               )",
    "  #1= #1 AND 123123.          ",
    "( a.var |= 0                    )",
    "  #1= #1 OR 0.                ",
    "( a.var *= 0                    )",
    "  #1= 0.                      ",
    "( a.var %= 1                    )",
    "  #1= #1 MOD 1.               ",
)
def test_augass1():
    a = p2g.Fixed(addr=1)
    a.var += 0
    a.var &= 123123
    a.var |= 0
    a.var -= 0
    a.var *= 0
    a.var /= 1
    a.var //= 1
    a.var %= 1
