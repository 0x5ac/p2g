import p2g
from conftest import want


PROBE = p2g.Fixed[3](addr=5061)


# pylint: disable=attribute-defined-outside-init,unneeded-not


def fn_nest2():
    PROBE.x = 111


def fn_nest1():
    PROBE.y = 2
    fn_nest2()
    PROBE.z = 3


class Table:
    def __init__(self):
        self.txyz = None
        self.txy = None
        self.v = None
        self.CURSOR = None
        pass


def add_some_symbols():
    st = Table()
    st.txyz = p2g.Var[3]()
    st.txy = p2g.Var[2]()
    st.CURSOR = p2g.Var[2]()
    st.v = p2g.Var()
    return st


# TESTS BELOW
########################################
@want(
    errors=[
        "test_smoke.py:9:4:6:     st.txyz.pop              ",
        "                         ^^                       ",
        "Bad axis letter in 'pop'.                         ",
    ]
)
def test_cerror_bad_attribute():
    st = add_some_symbols()
    st.txyz.pop


########################################
@want(
    errors=[
        "test_smoke.py:8:20:23:     T.var = T.var / 0.0    ",
        "Attempt to divide by zero.                 ^^^    ",
    ]
)
def test_cerror_div_err():
    T = p2g.Var()
    T.var = T.var / 0.0


########################################
@want(
    errors=[
        "test_smoke.py:10:24:25:     q = p2g.sys.address(p)  # noqa: F841",
        "Only vectors have addresses.                    ^ ",
    ]
)
def test_cerror_var_addresses():
    st = add_some_symbols()

    p = st.txyz.y
    q = p2g.sys.address(p)  # noqa: F841

    assert p2g.sys.address(st.txyz.y) == p2g.sys.address(101)

    assert p2g.sys.address(st.txyz.x) == p2g.sys.address(100)
    # negative assertions are because
    # if constant folding doesn't worke
    # the exp will be a tree, whch will
    # alwasy be true.
    assert not p2g.sys.address(st.txyz.z) == p2g.sys.address(202)
    assert not p2g.sys.address(PROBE) != p2g.sys.address(5061)
    assert p2g.sys.address(PROBE) == p2g.sys.address(5061)


########################################
@want(
    "O00001 (test_constant_arithmetic)                 ",
    "( v.xy = 9                      )                 ",
    "  #5061= 9.                                       ",
    "  #5062= 9.                                       ",
    "( assert sometrue.x == 1        )                 ",
    "  ( ok )                                          ",
    "( assert sometrue.y == 1        )                 ",
    "  ( ok )                                          ",
    "( assert sometrue.z == 0        )                 ",
    "  ( ok )                                          ",
    "( assert not t1                 )                 ",
    "  ( ok )                                          ",
    "( assert tmp.y == 13.3          )                 ",
    "  ( ok )                                          ",
    "( assert not any[tmp == [27.8, 40.2, -77.0]])     ",
    "  ( ok )                                          ",
    "  M30                                             ",
    "%                                                 ",
)
def test_constant_arithmetic():
    v = PROBE

    v.xy = 9

    zap0 = p2g.Const(9.2, 12.3, -10.0 - 17.0, 2)
    zap1 = p2g.Const(9.2, 12.3, -10.0 - 7.0, 2)
    zap2 = p2g.Const(9.2, 0, -10.0 - 7.0, 2)

    sometrue = zap0 == zap1
    # noinspection PyType:Checker

    f1 = zap0 == zap2  # noqa: F841

    #   btrue = any(zap0 == zap2)
    cfalse = all(zap0 == zap2)  # noqa: F841
    dtrue = all(zap0 == zap1)  # noqa: F841

    assert sometrue.x == 1
    assert sometrue.y == 1
    assert sometrue.z == 0

    #        assert (zap == zap2).y == 0

    tmp = zap0.xyz + 1
    #    tmp = round(zap.xyz * 4 - 9, 1)

    t1 = tmp.y != 13.3
    assert not t1

    assert tmp.y == 13.3
    #    assert not p2g.zap != [1, 2, 3]

    assert not any(tmp == [27.8, 40.2, -77.0])


########################################
@want(
    "O00001 (test_div_opts)                            ",
    "( T.var = T.var / -1.0          )                 ",
    "  #100= -#100                                     ",
    "  M30                                             ",
    "%                                                 ",
)
def test_div_opts():
    T = p2g.Var()
    T.var = T.var / 1.0
    T.var = T.var / -1.0


########################################
@want(
    "O00001 (test_fn_nest)                             ",
    "( PROBE.x = 1                   )                 ",
    "  #5061= 1.                                       ",
    "( PROBE.y = 2                   )                 ",
    "  #5062= 2.                                       ",
    "( PROBE.x = 111                 )                 ",
    "  #5061= 111.                                     ",
    "( PROBE.z = 3                   )                 ",
    "  #5063= 3.                                       ",
    "  M30                                             ",
    "%                                                 ",
)
def test_fn_nest():
    PROBE.x = 1
    fn_nest1()


########################################
@want(
    "O00001 (test_missing_functions)                   ",
    "( T.var = -T.var                )                 ",
    "  #100= -#100                                     ",
    "( T.var = ~T.var                )                 ",
    "  #100= #100 XOR -1.                              ",
    "( T.var = not T.var             )                 ",
    "  #100= #100 NE 0.                                ",
    "( T.var = -7                    )                 ",
    "  #100= -7.                                       ",
    "( T.var = ~7                    )                 ",
    "  #100= -8.                                       ",
    "( T.var = not 7                 )                 ",
    "  #100= 0.                                        ",
    "  M30                                             ",
    "%                                                 ",
)
def test_missing_functions():
    T = p2g.Var()
    T.var = -T.var
    T.var = ~T.var
    T.var = not T.var
    T.var = -7
    T.var = ~7
    T.var = not 7
    # assert g.checkcode(
    # "#100= -#100",
    # "#100= #100 XOR 0.",
    # "#100= #100 NE 0.",
    # "#100= -7.",
    # "#100= -8.",
    # "#100= 0.",
    # )


########################################
@want(
    "O00001 (test_operator_precedence)                 ",
    "( tmp.var = a.var / b.var % 7   )                 ",
    "  #100= [#1 / #2] MOD 7.                          ",
    "( tmp.var = a.var % b.var / 8   )                 ",
    "  #100= #1 MOD #2 / 8.                            ",
    "( tmp.var = [a.var / b.var] % 9 )                 ",
    "  #100= [#1 / #2] MOD 9.                          ",
    "( tmp.var = [a.var % b.var] / 10)                 ",
    "  #100= #1 MOD #2 / 10.                           ",
    "( tmp.var = a.var | b.var ^ c.var & d.var)        ",
    "  #100= #1 OR #2 XOR #3 AND #4                    ",
    "( tmp.var = a.var & b.var ^ c.var | d.var)        ",
    "  #100= #1 AND #2 XOR #3 OR #4                    ",
    "( tmp.var = 12                  )                 ",
    "  #100= 12.                                       ",
    "( src.y = 3                     )                 ",
    "  #5062= 3.                                       ",
    "( src.xy = 90                   )                 ",
    "  #5061= 90.                                      ",
    "  #5062= 90.                                      ",
    "( foo.var = 19                  )                 ",
    "  #333= 19.                                       ",
    "( st.txyz.x = 1 + 2 * 20 + 7 * 2)                 ",
    "  #100= 55.                                       ",
    "( src = ct.txyz.y               )                 ",
    "  #5061= #101                                     ",
    "  #5062= #101                                     ",
    "  #5063= #101                                     ",
    "( ct.txyz.z = [src + 2] * 20    )                 ",
    "  #102= [#5061 + 2.] * 20.                        ",
    "( ct.txyz.z = [ct.txyz.y + 2] * 20)               ",
    "  #102= [#101 + 2.] * 20.                         ",
    "( ct.txyz.y = ct.txyz.z + 2 + 3 )                 ",
    "  #101= #102 + 5.                                 ",
    "( ct.txyz.y = ct.txyz.z + 2 * 20 + 3  # ct.txyz.z +)",
    "  #101= #102 + 43.                                ",
    "( ct.txyz.y = ct.txyz.z + p2 * 2)                 ",
    "  #101= #102 + 34.                                ",
    "( ct.txyz.y = [ct.txyz.z + p2] * 2)               ",
    "  #101= [#102 + 17.] * 2.                         ",
    "( ct.txyz.y = ct.txyz.z + 3 - p2 * 2)             ",
    "  #101= #102 + 3. - 34.                           ",
    "  M30                                             ",
    "%                                                 ",
)
def test_operator_precedence():
    st = add_some_symbols()

    src = PROBE

    tmp = p2g.Fixed(addr=100)
    a = p2g.Fixed(addr=1)
    b = p2g.Fixed(addr=2)
    c = p2g.Fixed(addr=3)
    d = p2g.Fixed(addr=4)

    #        sac.ob(g)

    # gcode has unusal precendence for %
    # make sure translated from python to gcode
    # nicely

    tmp.var = a.var / b.var % 7
    tmp.var = a.var % b.var / 8
    tmp.var = (a.var / b.var) % 9
    tmp.var = (a.var % b.var) / 10

    # same as python
    tmp.var = a.var | b.var ^ c.var & d.var
    tmp.var = a.var & b.var ^ c.var | d.var

    # goes ((pointer to (float)*1):100)
    # [(contents of ((pointer to (float)*1):100))]
    tmp.var = 12
    src.y = 3

    src.xy = 90
    foo = p2g.Fixed(addr=333)
    foo.var = 19

    st.txyz.x = 1 + 2 * 20 + 7 * 2
    ct = st
    src = ct.txyz.y

    ct.txyz.z = (src + 2) * 20
    ct.txyz.z = (ct.txyz.y + 2) * 20

    ct.txyz.y = ct.txyz.z + 2 + 3
    ct.txyz.y = ct.txyz.z + 2 * 20 + 3  # ct.txyz.z +
    p2 = 17.0
    ct.txyz.y = ct.txyz.z + p2 * 2
    ct.txyz.y = (ct.txyz.z + p2) * 2
    ct.txyz.y = ct.txyz.z + 3 - p2 * 2


########################################
@want(
    "O00001 (test_prev_errors)                         ",
    "( dst = Var[its]  # noqa: F841  )                 ",
    "  #106= [#100 - #103] / 2.                        ",
    "  M30                                             ",
    "%                                                 ",
)
def test_prev_errors():
    class S:
        def __init__(self):
            self.MAX = p2g.Var[3]()
            self.MIN = p2g.Var[3]()
            self.delta = 1.0

    s = S()

    itsvec = p2g.Const[2]((s.MAX.xy - s.MIN.xy) / 2.0 / s.delta)
    its = itsvec[0]
    dst = p2g.Var(its)  # noqa: F841


########################################
@want(
    errors=[
        "test_smoke.py:8:4:7:     p2g.base_addr(300)       ",
        "                         ^^^                      ",
        "module 'p2g' has no attribute 'base_addr'         ",
    ]
)
def test_simple_code0():
    p2g.base_addr(300)

    CURSOR = p2g.Var(20, 30)
    #    CURSOR = [1, 7]
    CURSOR.xy += [71, 17]
    CURSOR.y = PROBE.y - 10
    CURSOR.x = CURSOR.y

    CURSOR.y = 901
    CURSOR[0:2] = PROBE.xy * 2.0


########################################
@want(
    "O00001 (test_simplify0_fail)                      ",
    "( cursor.xy += delta            )                 ",
    "  #200= #200 + 1.                                 ",
    "  #201= #201 - 2.                                 ",
    "  M30                                             ",
    "%                                                 ",
)
def test_simplify0_fail():
    dx, dy = -1, -1
    howtosearch = p2g.Const[2](-1.0, 2.0)
    cursor = p2g.Fixed[2](addr=200)
    delta = howtosearch * [dx, dy]

    cursor.xy += delta


########################################
@want(
    "O00001 (test_simplify1_fail)                      ",
    "( x = Var[y[0] + -1 * 1.5]  # noqa: F841)         ",
    "  #100= #17 - 1.5                                 ",
    "  M30                                             ",
    "%                                                 ",
)
def test_simplify1_fail():
    y = p2g.Fixed[1](addr=17)
    x = p2g.Var(y[0] + -1 * 1.5)  # noqa: F841


########################################
@want(
    "O00001 (test_tuples)                              ",
    "( PROBE.x, PROBE.y = 1, 2       )                 ",
    "  #5061= 1.                                       ",
    "  #5062= 2.                                       ",
    "  M30                                             ",
    "%                                                 ",
)
def test_tuples():
    PROBE.x, PROBE.y = 1, 2


########################################
@want(
    "O00001 (test_variable_assignment)                 ",
    "( st.txyz.xy = [1, 3 + 9]       )                 ",
    "  #100= 1.                                        ",
    "  #101= 12.                                       ",
    "( st.txyz.z = st.txyz.y + 1     )                 ",
    "  #102= #101 + 1.                                 ",
    "( st.txyz.y = 9                 )                 ",
    "  #101= 9.                                        ",
    "( st.txyz.x = [1]               )                 ",
    "  #100= 1.                                        ",
    "( st.txyz.xyz = [1, 2, 3]       )                 ",
    "  #100= 1.                                        ",
    "  #101= 2.                                        ",
    "  #102= 3.                                        ",
    "( st.txyz.xyz = [st.txy.x + 1, st.txy.y * 34, 99])",
    "  #100= #103 + 1.                                 ",
    "  #101= #104 * 34.                                ",
    "  #102= 99.                                       ",
    "  M30                                             ",
    "%                                                 ",
)
def test_variable_assignment():
    st = add_some_symbols()
    st.txyz.xy = [1, 3 + 9]

    st.txyz.z = st.txyz.y + 1

    st.txyz.y = 9

    st.txyz.x = [1]

    st.txyz.xyz = [1, 2, 3]
    st.txyz.xyz = [st.txy.x + 1, st.txy.y * 34, 99]


########################################
@want(
    "O00001 (test_wibble)                              ",
    "( CURSOR = Fixed[1, 2, 3, addr=100]  # noqa: F841)",
    "  #100= 1.                                        ",
    "  #101= 2.                                        ",
    "  #102= 3.                                        ",
    "  M30                                             ",
    "%                                                 ",
)
def test_wibble():
    CURSOR = p2g.Fixed(1, 2, 3, addr=100)  # noqa: F841
