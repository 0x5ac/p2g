import p2g
from conftest import want

print = p2g.sys.print


class F:
    def __init__(self):
        self.a = 2
        self.b = 3


f = F()

# TESTS BELOW
########################################
@want(
    "O00001 (test_array)                               ",
    "DPRNT[#110[42]#111[42]#112[42]]                   ",
    "DPRNT[#110[12]#111[12]#112[12]]                   ",
    "  M30                                             ",
    "%                                                 ",
)
def test_array():
    v = p2g.Fixed[3](addr=110)

    print(f"{v:7.2f}")
    print(f"{v:4.2f}")


########################################
@want(
    "O00001 (test_array0)                              ",
    "DPRNT[#110[42]XY#111[42]XY#112[42]X]              ",
    "  M30                                             ",
    "%                                                 ",
)
def test_array0():
    v = p2g.Fixed[3](addr=110)
    print(f"{v:####.##X?Y}")


########################################
@want(
    "O00001 (test_array1)                              ",
    "DPRNT[Xabc#110[10]def,*Yabc#111[10]def,*Zabc#112[10]def,*]",
    "  M30                                             ",
    "%                                                 ",
)
def test_array1():
    v = p2g.Fixed[3](addr=110)
    print(f"{v:@abc#def, ?}")


########################################
@want(
    "O00001 (test_array2)                              ",
    "DPRNT[#110[22],*#111[22],*#112[22]]               ",
    "  M30                                             ",
    "%                                                 ",
)
def test_array2():
    v = p2g.Fixed[3](addr=110)
    print(f"{v:##.##?, }")


########################################
@want(
    "O00001 (test_array3)                              ",
    "DPRNT[0:#110[32],*1:#111[32],*2:#112[32]]         ",
    "  M30                                             ",
    "%                                                 ",
)
def test_array3():
    v = p2g.Fixed[3](addr=110)
    print(f"{v:!:###.##?, }")


########################################
@want(
    "O00001 (test_array4)                              ",
    "DPRNT[X=#110[32]*Y=#111[32]*Z=#112[32]]           ",
    "  M30                                             ",
    "%                                                 ",
)
def test_array4():
    v = p2g.Fixed[3](addr=110)
    print(f"{v:@=###.##? }")


########################################
@want(
    "O00001 (test_array_py0)                           ",
    "DPRNT[#110[12]#111[12]#112[12]]                   ",
    "  M30                                             ",
    "%                                                 ",
)
def test_array_py0():
    v = p2g.Fixed[3](addr=110)
    print(f"{v:4.2f}")


########################################
@want(
    "O00001 (test_consts)                              ",
    "DPRNT[C**12.340Y**2.000Y**3.000Y]                 ",
    "  M30                                             ",
    "%                                                 ",
)
def test_consts():
    src = p2g.Const(12.34, 2, 3)
    v = p2g.Fixed[3](addr=110)
    p2g.sys.print(f"C {src:###.###Y}")


########################################
@want(
    "O00001 (test_from_self)                           ",
    "DPRNT[abc***2.00def***3.00ghi]                    ",
    "  M30                                             ",
    "%                                                 ",
)
def test_from_self():
    p2g.sys.print(f"abc{f.a}def{f.b}ghi")


########################################
@want(
    "O00001 (test_many_consts)                         ",
    "DPRNT[abc**17.00def**20.00ghi]                    ",
    "  M30                                             ",
    "%                                                 ",
)
def test_many_consts():
    f = 17
    g = 20
    p2g.sys.print(f"abc{f}def{g}ghi")


########################################
@want(
    "O00001 (test_multiple)                            ",
    "( j = Var[99]                   )                 ",
    "  #100= 99.                                       ",
    '( sys.print[f"{j+12}"]          )                 ',
    "  #101= #100 + 12.                                ",
    "DPRNT[#101[42]]                                   ",
    '( sys.print[f"{j+12}"]          )                 ',
    "  #101= #100 + 12.                                ",
    "DPRNT[#101[42]]                                   ",
    '( sys.print[f"{j+12}"]          )                 ',
    "  #101= #100 + 12.                                ",
    "DPRNT[#101[42]]                                   ",
    "  M30                                             ",
    "%                                                 ",
)
def test_multiple():
    j = p2g.Var(99)
    p2g.sys.print(f"{j+12}")
    p2g.sys.print(f"{j+12}")
    p2g.sys.print(f"{j+12}")


########################################
@want(
    "O00001 (test_simple0)                             ",
    "DPRNT[#110[53]]                                   ",
    "  M30                                             ",
    "%                                                 ",
)
def test_simple0():
    v = p2g.Fixed(addr=110)
    print(f"{v:f}")


########################################
@want(
    "O00001 (test_simple1)                             ",
    "DPRNT[#110[42]]                                   ",
    "  M30                                             ",
    "%                                                 ",
)
def test_simple1():
    v = p2g.Fixed(addr=110)
    print(f"{v}")


########################################
@want(
    "O00001 (test_simple_expression)                   ",
    "( j = Var[99]                   )                 ",
    "  #100= 99.                                       ",
    '( sys.print[f"{j+12}"]          )                 ',
    "  #101= #100 + 12.                                ",
    "DPRNT[#101[42]]                                   ",
    "  M30                                             ",
    "%                                                 ",
)
def test_simple_expression():
    j = p2g.Var(99)
    p2g.sys.print(f"{j+12}")


########################################
@want(
    "O00001 (test_simple_expression0)                  ",
    "( j = Var[99]                   )                 ",
    "  #100= 99.                                       ",
    "( k = Var[j + 12]               )                 ",
    "  #101= #100 + 12.                                ",
    "DPRNT[#101[42]]                                   ",
    "  M30                                             ",
    "%                                                 ",
)
def test_simple_expression0():
    j = p2g.Var(99)
    k = p2g.Var(j + 12)
    p2g.sys.print(f"{k}")


########################################
@want(
    "O00001 (test_simple_hand_expanded_expression0)    ",
    "( j = Var[99]                   )                 ",
    "  #100= 99.                                       ",
    "( k = Var[j + 12]               )                 ",
    "  #101= #100 + 12.                                ",
    "DPRNT[#101[42]]                                   ",
    "  M30                                             ",
    "%                                                 ",
)
def test_simple_hand_expanded_expression0():
    j = p2g.Var(99)
    k = p2g.Var(j + 12)
    p2g.sys.print(f"{k}")


########################################
@want(
    "O00001 (test_simple_number)                       ",
    "( j = Var[99]                   )                 ",
    "  #100= 99.                                       ",
    "( k = Var[j + 12]               )                 ",
    "  #101= #100 + 12.                                ",
    "DPRNT[#101[42]]                                   ",
    "  M30                                             ",
    "%                                                 ",
)
def test_simple_number():
    j = p2g.Var(99)
    k = p2g.Var(j + 12)
    p2g.sys.print(f"{k}")

    # j = p2g.Var(99)
    # p2g.sys.print(f"{j}")


########################################
@want(
    "O00001 (test_simple_text)                         ",
    "DPRNT[abcdef]                                     ",
    "  M30                                             ",
    "%                                                 ",
)
def test_simple_text():
    p2g.sys.print("abc" + "def")
