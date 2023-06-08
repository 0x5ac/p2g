#! /usr/bin/env python

import p2g


PROBE = p2g.Fixed[3](addr=5061)


# pylint: disable=attribute-defined-outside-init,unneeded-not


@p2g.inline
def fn_nest2():
    PROBE.x = 111


@p2g.inline
def fn_nest1():
    PROBE.y = 2
    fn_nest2()
    PROBE.z = 3


def add_some_symbols():
    st = p2g.Table()
    st.txyz = p2g.Var[3]()
    st.txy = p2g.Var[2]()
    st.CURSOR = p2g.Var[2]()
    st.v = p2g.Var()
    return st


@p2g.must_be(
    "Bad axis letter in 'pop'",
    "p2g/tests/test_smoke.py:8:4:6:     st.txyz.pop",
    "                                   ^^",
)
def test_comperr_bad_attribute():
    st = add_some_symbols()
    st.txyz.pop


@p2g.must_be(
    "Attempt to divide by zero.",
    "p2g/tests/test_smoke.py:8:20:23:     T.var = T.var / 0.0",
    "                                                     ^^^",
)
def test_comperr_div_err():
    T = p2g.Var()
    T.var = T.var / 0.0


@p2g.must_be(
    "( v.xy = 9                      )",
    "  #5061= 9.",
    "  #5062= 9.",
)
def test_constant_arithmetic():
    v = PROBE

    v.xy = 9

    zap0 = p2g.Const(9.2, 12.3, -10.0 - 17.0, 2)
    zap1 = p2g.Const(9.2, 12.3, -10.0 - 7.0, 2)
    zap2 = p2g.Const(9.2, 0, -10.0 - 7.0, 2)

    sometrue = zap0 == zap1
    # noinspection PyType:Checker

    f1 = zap0 == zap2

    #   btrue = any(zap0 == zap2)
    cfalse = all(zap0 == zap2)
    dtrue = all(zap0 == zap1)

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


@p2g.must_be(
    "( T.var = T.var / -1.0          )",
    "  #100= -#100",
)
def test_div_opts():
    T = p2g.Var()
    T.var = T.var / 1.0
    T.var = T.var / -1.0


@p2g.must_be(
    "( PROBE.x = 1                   )",
    "  #5061= 1.",
    "( PROBE.y = 2                   )",
    "  #5062= 2.",
    "( PROBE.x = 111                 )",
    "  #5061= 111.",
    "( PROBE.z = 3                   )",
    "  #5063= 3.",
)
def test_fn_nest():
    PROBE.x = 1
    fn_nest1()


@p2g.must_be(
    "( T.var = -T.var                )",
    "  #100= -#100",
    "( T.var = ~T.var                )",
    "  #100= #100 XOR -1.",
    "( T.var = not T.var             )",
    "  #100= #100 NE 0.",
    "( T.var = -7                    )",
    "  #100= -7.",
    "( T.var = ~7                    )",
    "  #100= -8.",
    "( T.var = not 7                 )",
    "  #100= 0.",
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


@p2g.must_be(
    "( tmp.var = a.var / b.var % 7   )",
    "  #100= [#1 / #2] MOD 7.",
    "( tmp.var = a.var % b.var / 8   )",
    "  #100= #1 MOD #2 / 8.",
    "( tmp.var = [a.var / b.var] % 9 )",
    "  #100= [#1 / #2] MOD 9.",
    "( tmp.var = [a.var % b.var] / 10)",
    "  #100= #1 MOD #2 / 10.",
    "( tmp.var = a.var | b.var ^ c.var & d.var)",
    "  #100= #1 OR #2 XOR #3 AND #4",
    "( tmp.var = a.var & b.var ^ c.var | d.var)",
    "  #100= #1 AND #2 XOR #3 OR #4",
    "( tmp.var = 12                  )",
    "  #100= 12.",
    "( src.y = 3                     )",
    "  #5062= 3.",
    "( src.xy = 90                   )",
    "  #5061= 90.",
    "  #5062= 90.",
    "( foo.var = 19                  )",
    "  #333= 19.",
    "( st.txyz.x = 1 + 2 * 20 + 7 * 2)",
    "  #100= 55.",
    "( src = ct.txyz.y               )",
    "  #5061= #101",
    "  #5062= #101",
    "  #5063= #101",
    "( ct.txyz.z = [src + 2] * 20    )",
    "  #102= [#5061 + 2.] * 20.",
    "( ct.txyz.z = [ct.txyz.y + 2] * 20)",
    "  #102= [#101 + 2.] * 20.",
    "( ct.txyz.y = ct.txyz.z + 2 + 3 )",
    "  #101= #102 + 5.",
    "( ct.txyz.y = ct.txyz.z + 2 * 20 + 3  # ct.txyz.z +)",
    "  #101= #102 + 43.",
    "( ct.txyz.y = ct.txyz.z + p2 * 2)",
    "  #101= #102 + 34.",
    "( ct.txyz.y = [ct.txyz.z + p2] * 2)",
    "  #101= [#102 + 17.] * 2.",
    "( ct.txyz.y = ct.txyz.z + 3 - p2 * 2)",
    "  #101= #102 + 3. - 34.",
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


@p2g.must_be(
    "( dst = p2Var[its]              )",
    "  #106= [#100 - #103] / 2.",
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
    dst = p2g.Var(its)


@p2g.must_be(
    "( CURSOR = p2Var[20, 30]        )",
    "  #300= 20.",
    "  #301= 30.",
    "( CURSOR.xy += [71, 17]         )",
    "  #300= #300 + 71.",
    "  #301= #301 + 17.",
    "( CURSOR.y = PROBE.y - 10       )",
    "  #301= #5062 - 10.",
    "( CURSOR.x = CURSOR.y           )",
    "  #300= #301",
    "( CURSOR.y = 901                )",
    "  #301= 901.",
    "( CURSOR[0:2] = PROBE.xy * 2.0  )",
    "  #300= #5061 * 2.",
    "  #301= #5062 * 2.",
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


@p2g.must_be(
    "( cursor.xy += delta            )",
    "  #200= #200 + 1.",
    "  #201= #201 - 2.",
)
def test_simplify0_fail():
    dx, dy = -1, -1
    howtosearch = p2g.Const[2](-1.0, 2.0)
    cursor = p2g.Fixed[2](addr=200)
    delta = howtosearch * [dx, dy]

    cursor.xy += delta


@p2g.must_be(
    "( x = p2Var[y[0] + -1 * 1.5]    )",
    "  #100= #17 - 1.5",
)
def test_simplify1_fail():
    y = p2g.Fixed[1](addr=17)
    x = p2g.Var(y[0] + -1 * 1.5)


@p2g.must_be(
    "( PROBE.x, PROBE.y = 1, 2       )",
    "  #5061= 1.",
    "  #5062= 2.",
)
def test_tuples():
    PROBE.x, PROBE.y = 1, 2


@p2g.must_be()
def test_var_addresses():
    st = add_some_symbols()

    p = st.txyz.y
    q = p2g.address(p)

    assert p2g.address(st.txyz.y) == p2g.as_address(101)

    assert p2g.address(st.txyz.x) == p2g.as_address(100)
    # negative assertions are because
    # if constant folding doesn't worke
    # the exp will be a tree, whch will
    # alwasy be true.
    assert not p2g.address(st.txyz.z) == p2g.as_address(202)
    assert not p2g.address(PROBE) != p2g.as_address(5061)
    assert p2g.address(PROBE) == p2g.as_address(5061)


@p2g.must_be(
    "( st.txyz.xy = [1, 3 + 9]       )",
    "  #100= 1.",
    "  #101= 12.",
    "( st.txyz.z = st.txyz.y + 1     )",
    "  #102= #101 + 1.",
    "( st.txyz.y = 9                 )",
    "  #101= 9.",
    "( st.txyz.x = [1]               )",
    "  #100= 1.",
    "( st.txyz.xyz = [1, 2, 3]       )",
    "  #100= 1.",
    "  #101= 2.",
    "  #102= 3.",
    "( st.txyz.xyz = [st.txy.x + 1, st.txy.y * 34, 99])",
    "  #100= #103 + 1.",
    "  #101= #104 * 34.",
    "  #102= 99.",
)
def test_variable_assignment():
    st = add_some_symbols()
    st.txyz.xy = [1, 3 + 9]

    st.txyz.z = st.txyz.y + 1

    st.txyz.y = 9

    st.txyz.x = [1]

    st.txyz.xyz = [1, 2, 3]
    st.txyz.xyz = [st.txy.x + 1, st.txy.y * 34, 99]


@p2g.must_be(
    "( CURSOR = p2Fixed[1, 2, 3, addr=100])",
    "  #100= 1.",
    "  #101= 2.",
    "  #102= 3.",
)
def test_wibble():
    CURSOR = p2g.Fixed(1, 2, 3, addr=100)
