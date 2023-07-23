import p2g


@p2g.must_be(
    "                              ( x[y[z + 10]] = x[y[z + 8]]    )",
    "  #[#[#111 + 120] + 100]= #[#[#111 + 118] + 100]",
)
def test_nested1c():
    x = p2g.Fixed[10](addr=100)
    y = p2g.Fixed[10](addr=110)
    z = p2g.Fixed(addr=111)
    x[y[z + 10]] = x[y[z + 8]]


def add_some_symbols():
    st = p2g.Table()
    st.txyz = p2g.Var[3]()
    st.txy = p2g.Var[2]()
    st.CURSOR = p2g.Var[2]()
    st.v = p2g.Var()
    return st


@p2g.must_be(
    "(     addr=20,                  )",
    "  #20= 150.",
    "( sa = Fixed[[1, 2, 3.14, 4, 5, 6], addr=40])",
    "  #40= 1.",
    "  #41= 2.",
    "  #42= 3.14",
    "  #43= 4.",
    "  #44= 5.",
    "  #45= 6.",
    "( for j in range[3]:            )",
    "  #109= 0.",
    "L1000",
    "  IF [#109 GE 3.] GOTO 1002",
    "(     ptr[j.var + 2] = [j + 2] ** 2 + 17)",
    "  #[#109 + 402]= POW[#109 + 2.,2.] + 17.",
    "  #109= #109 + 1.",
    "  GOTO 1000",
    "L1002",
)
def test_const_deref_addresses():
    st = add_some_symbols()
    ptrb = st.txyz

    idx = p2g.Fixed(
        150,
        addr=20,
    )

    sa = p2g.Fixed([1, 2, 3.14, 4, 5, 6], addr=40)
    ptr = p2g.Fixed[100](addr=400)

    j = p2g.Fixed(addr=10)
    for j in range(3):
        ptr[j.var + 2] = (j + 2) ** 2 + 17


@p2g.must_be(
    "Bad axis letter in 'pop'",
    "p2g/tests/test_vector.py:9:4:6:     st.txyz.pop",
    "                                    ^^",
)
def test_comperr_bad_attribute():
    #    with pytest.raises(AttributeError):
    st = add_some_symbols()
    st.txyz.pop


@p2g.must_be(
    "Reference to too many axes.",
    "p2g/tests/test_vector.py:10:4:6:     st.txy.xyz = 0x99",
    "                                     ^^",
)
def test_comperr_bad_bounds0():
    st = add_some_symbols()

    #    with pytest.raises(AttributeError):
    st.txy.xyz = 0x99


@p2g.must_be(
    "Reference to too many axes.",
    "p2g/tests/test_vector.py:9:17:19:     st.txyz.xy = st.txy.z",
    "                                                   ^^",
)
def test_comperr_bad_bounds1():
    st = add_some_symbols()

    st.txyz.xy = st.txy.z


@p2g.must_be(
    "( x[y[:]] = x[y[z + 10]]        )",
    "  #[#110 + 100]= #[#[#111 + 120] + 100]",
    "  #[#111 + 100]= #[#[#111 + 120] + 100]",
    "  #[#112 + 100]= #[#[#111 + 120] + 100]",
    "  #[#113 + 100]= #[#[#111 + 120] + 100]",
    "  #[#114 + 100]= #[#[#111 + 120] + 100]",
    "  #[#115 + 100]= #[#[#111 + 120] + 100]",
    "  #[#116 + 100]= #[#[#111 + 120] + 100]",
    "  #[#117 + 100]= #[#[#111 + 120] + 100]",
    "  #[#118 + 100]= #[#[#111 + 120] + 100]",
    "  #[#119 + 100]= #[#[#111 + 120] + 100]",
)
def test_nested3():
    x = p2g.Fixed[10](addr=100)
    y = p2g.Fixed[10](addr=110)
    z = p2g.Fixed(addr=111)
    x[y[:]] = x[y[z + 10]]


@p2g.must_be(
    "Index out of range, index=20 size=10",
    "p2g/tests/test_vector.py:9:6:8:     x[20] = 9",
    "                                      ^^",
)
def test_comperr_oob():
    x = p2g.Fixed[10]()
    # with pytest.raises(IndexError):
    x[20] = 9


@p2g.must_be(
    "  ( Fixed[1, 2, 3, addr=100]    )",
    "  #100= 1.",
    "  #101= 2.",
    "  #102= 3.",
)
def test_fixedvec0():
    p2g.Fixed(1, 2, 3, addr=100)


@p2g.must_be(
    "                ( Fixed[3][1, 2, 3, addr=100] )",
    "  #100= 1.    ",
    "  #101= 2.",
    "  #102= 3.",
)
def test_fixedvec1():
    p2g.Fixed[3](1, 2, 3, addr=100)


@p2g.must_be(
    "( x[z] = y[z]                   )",
    "  #[#111 + 100]= #[#111 + 110]",
)
def test_nested0():
    x = p2g.Fixed[10](addr=100)
    y = p2g.Fixed[10](addr=110)
    z = p2g.Fixed(addr=111)
    x[z] = y[z]


@p2g.must_be(
    "( x[y[z + 10]] = y[x[z] + 10]   )    ",
    "  #[#[#111 + 120] + 100]= #[#[#111 + 100] + 120]",
)
def test_nested1a():
    x = p2g.Fixed[10](addr=100)
    y = p2g.Fixed[10](addr=110)
    z = p2g.Fixed(addr=111)
    x[y[z + 10]] = y[x[z] + 10]


@p2g.must_be()
def test_nested1b():
    x = p2g.Fixed[10](addr=100)
    y = p2g.Fixed[10](addr=110)
    z = p2g.Fixed(addr=111)
    x[y[z + 10]] = x[y[z + 10]]


@p2g.must_be()
def test_nested1d():
    x = p2g.Fixed[10](addr=100)
    y = p2g.Fixed[10](addr=110)
    z = p2g.Fixed(addr=111)
    x[y[z + 10]] = x[y[z + 10]]


@p2g.must_be(
    "                              ( x[y[z]] = y[x[z]]             )",
    "  #[#[#111 + 110] + 100]= #[#[#111 + 100] + 110]",
)
def test_nested1():
    x = p2g.Fixed[10](addr=100)
    y = p2g.Fixed[10](addr=110)
    z = p2g.Fixed(addr=111)
    x[y[z]] = y[x[z]]


@p2g.must_be(
    "( nw = Fixed[7][2, 2, 2, 2, 3, 3, 1, addr=200])",
    "  #200= 2.",
    "  #201= 2.",
    "  #202= 2.",
    "  #203= 2.",
    "  #204= 3.",
    "  #205= 3.",
    "  #206= 1.",
    "( nw[2] = 3                     )",
    "  #202= 3.",
    "( nw[4] = 9                     )",
    "  #204= 9.",
    "( idx = Fixed[7, addr=220]      )",
    "  #220= 7.",
    "( fish.var = nw[idx // 1]       )",
    "  #300= #[#220 + 200]",
)
def test_simple_arrays():
    nw = p2g.Fixed[7](2, 2, 2, 2, 3, 3, 1, addr=200)
    nw[2] = 3
    nw[4] = 9
    idx = p2g.Fixed(7, addr=220)
    fish = p2g.Fixed(addr=300)
    fish.var = nw[idx // 1]


@p2g.must_be(
    "( for j in range[7, 10]:        )",
    "  #102= 7.",
    "L1000",
    "  IF [#102 GE 10.] GOTO 1002",
    "(     ptr[j] = 12               )",
    "  #[#102 + 300]= 12.",
    "  #102= #102 + 1.",
    "  GOTO 1000",
    "L1002",
    "( for j in range[7, 10]:        )",
    "  #112= 7.",
    "L1003",
    "  IF [#112 GE 10.] GOTO 1005",
    "(     ptr[j] = j                )",
    "  #[#112 + 300]= #112",
    "  #112= #112 + 1.",
    "  GOTO 1003",
    "L1005",
    "( for j in range[2, 7]:         )",
    "  #114= 2.",
    "L1006",
    "  IF [#114 GE 7.] GOTO 1008",
    "(     ptr[j] = [j + 2] ** 2 + 17)",
    "  #[#114 + 300]= POW[#114 + 2.,2.] + 17.",
    "  #114= #114 + 1.",
    "  GOTO 1006",
    "L1008",
)
def test_var_deref_addresses():
    j = p2g.Var()

    ptr = p2g.Fixed[10](addr=300)

    for j in range(7, 10):
        ptr[j] = 12

    st = add_some_symbols()

    ptr1 = p2g.address(st.txyz.xyz)

    ptr2 = st.txyz

    assert ptr1 == ptr2
    assert ptr2 == st.txyz

    assert not (p2g.address(ptr2.x) != p2g.address(st.txyz.x))
    assert ptr1 == st.txyz

    assert p2g.address(st.txyz.xyz) == st.txyz

    for j in range(7, 10):
        ptr[j] = j

    for j in range(2, 7):
        ptr[j] = (j + 2) ** 2 + 17


@p2g.must_be(
    " ( x[x.xy] = x.xy                )",
    "  #[#100 + 100]= #100        ",
    "  #[#101 + 100]= #101",
)
def test_wacky_0():
    x = p2g.Fixed[10](addr=100)
    x[x.xy] = x.xy


@p2g.must_be(
    " ( x[x.xy] = x.x                 )",
    "  #[#100 + 100]= #100        ",
    "  #[#101 + 100]= #100",
)
def test_wacky_1():
    x = p2g.Fixed[10](addr=100)
    x[x.xy] = x.x


@p2g.must_be(
    "( x = Fixed[0, 1, 2, 3, 4, 5, addr=300])",
    "  #300= 0.",
    "  #301= 1.",
    "  #302= 2.",
    "  #303= 3.",
    "  #304= 4.",
    "  #305= 5.",
    "( y[:] = x[::2]                 )",
    "  #400= #300",
    "  #401= #302",
    "  #402= #304",
)
def test_slice_step0():
    x = p2g.Fixed(0, 1, 2, 3, 4, 5, addr=300)
    y = p2g.Fixed[3](addr=400)

    y[:] = x[::2]


@p2g.must_be(
    "( y[:] = x[:-4]                 )",
    "  #400= #300",
    "  #401= #301",
    "  #402= #302",
    "  #403= #303",
    "  #404= #304",
    "  #405= #305",
    "  #406= #300",
    "  #407= #301",
    "  #408= #302",
    "  #409= #303",
)
def test_slice_negend():
    x = p2g.Fixed[10](addr=300)
    y = p2g.Fixed[10](addr=400)

    y[:] = x[:-4]


@p2g.must_be(
    "( y[1:5:2] = x[1:7:3]           )",
    "  #401= #301",
    "  #403= #304",
)
def test_slice_all():
    x = p2g.Fixed[10](addr=300)
    y = p2g.Fixed[10](addr=400)

    y[1:5:2] = x[1:7:3]


@p2g.must_be(
    "( mx = Var[flutes[0]]           )",
    "  #101= #200",
    "( for i in flutes[1:]:          )",
    "  #102= 201.",
    "L1000",
    "  IF [#102 GE 210.] GOTO 1002",
    "  #100= #[#102]",
    "(     if i > mx:                )",
    "  IF [#100 LE #101] GOTO 1003",
    "(         mx = i                )",
    "  #101= #100",
    "  GOTO 1004",
    "L1003",
    "L1004",
    "  #102= #102 + 1.",
    "  GOTO 1000",
    "L1002",
)
def test_find_flutes():
    i = p2g.Var()
    flutes = p2g.Fixed[10](addr=200)
    mx = p2g.Var(flutes[0])
    for i in flutes[1:]:
        if i > mx:
            mx = i


def max(a, b):
    return a if a > b else b


TOOL_TBL_FLUTES = p2g.Fixed[100](addr=300)
MESSAGE = p2g.Fixed(addr=3006)


@p2g.must_be(
    "( mx = Var[TOOL_TBL_FLUTES[0]]  )",
    "  #100= #300",
    "( for i in TOOL_TBL_FLUTES[1:]: )",
    "  #101= 301.",
    "L1000",
    "  IF [#101 GE 400.] GOTO 1002",
    "(     mx = max[mx, i]           )",
    "  #100= #100 * [#100 GT #[#101]] + #[#101] * [#100 LE #[#101]]",
    "  #101= #101 + 1.",
    "  GOTO 1000",
    "L1002",
    "( MESSAGE.var = mx              )",
    "  #3006= #100",
)
def test_find_max_way2():
    # stop with alarm code as max # flutes in table.

    mx = p2g.Var(TOOL_TBL_FLUTES[0])
    for i in TOOL_TBL_FLUTES[1:]:
        mx = max(mx, i)

    MESSAGE.var = mx
