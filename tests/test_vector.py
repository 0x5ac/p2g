import p2g

from conftest import want


def max(a, b):
    return a if a > b else b


TOOL_TBL_FLUTES = p2g.Fixed[100](addr=300)
MESSAGE = p2g.Fixed(addr=3006)


class ITable:
    txyz: p2g.Vec
    txy: p2g.Vec
    CURSOR: p2g.Vec
    v: p2g.Vec


def add_some_symbols():
    st = ITable()
    st.txyz = p2g.Var[3]()
    st.txy = p2g.Var[2]()
    st.CURSOR = p2g.Var[2]()
    st.v = p2g.Var()
    return st


# TESTS BELOW
########################################
@want(
    errors=[
        "test_vector.py:9:10:11:     k = j[5]              ",
        "                                  ^               ",
        "Index out of range, index=5 size=3.               ",
    ]
)
def test_bad_index_1():
    j = p2g.Var[3](1, 2, 3)
    k = j[5]


########################################
@want(
    errors=[
        "test_vector.py:10:4:6:     st.txyz.popfishdog",
        "                           ^^",
        "Bad axis letter in 'popfishdog'.        ",
    ]
)
def test_cerror_bad_attribute():
    #    with pytest.raises(AttributeError):
    st = add_some_symbols()
    st.txyz.popfishdog


########################################
@want(
    errors=[
        "test_vector.py:11:4:6:     st.txy.xyz = 0x99      ",
        "                           ^^                     ",
        "Reference to too many axes.                       ",
    ]
)
def test_cerror_bad_bounds0():
    st = add_some_symbols()

    #    with pytest.raises(AttributeError):
    st.txy.xyz = 0x99


########################################
@want(
    errors=[
        "test_vector.py:9:17:19:     st.txyz.xy = st.txy.z ",
        "Reference to too many axes.              ^^       ",
    ]
)
def test_cerror_bad_bounds1():
    st = add_some_symbols()

    st.txyz.xy = st.txy.z


########################################
@want(
    errors=[
        "test_vector.py:7:18:20:     x = p2g.Fixed[10]()   ",
        "Fixed needs an address.                   ^^      ",
    ]
)
def test_cerror_oob():
    x = p2g.Fixed[10]()
    # with pytest.raises(IndexError):
    x[20] = 9


########################################
@want(
    "O00001 (test_const_deref_addresses)               ",
    "(     addr=20,                  )                 ",
    "  #20= 150.                                       ",
    "( Fixed[[1, 2, 3.14, 4, 5, 6], addr=40])          ",
    "  #40= 1.                                         ",
    "  #41= 2.                                         ",
    "  #42= 3.14                                       ",
    "  #43= 4.                                         ",
    "  #44= 5.                                         ",
    "  #45= 6.                                         ",
    "( for j in range[3]:            )                 ",
    "  #109= 0.                                        ",
    "N1000                                             ",
    "( for j in range[3]:            )                 ",
    "  IF [#109 GE 3.] GOTO 1002                       ",
    "(     ptr[j.var + 2] = [j + 2] ** 2 + 17)         ",
    "  #[#109 + 402]= POW[#109 + 2.,2.] + 17.          ",
    "  #109= #109 + 1.                                 ",
    "  GOTO 1000                                       ",
    "N1002                                             ",
    "  M30                                             ",
    "%                                                 ",
)
def test_const_deref_addresses():
    st = add_some_symbols()
    ptrb = st.txyz  # noqa: F841

    p2g.Fixed(
        150,
        addr=20,
    )

    p2g.Fixed([1, 2, 3.14, 4, 5, 6], addr=40)
    ptr = p2g.Fixed[100](addr=400)

    j = p2g.Fixed(addr=10)
    for j in range(3):
        ptr[j.var + 2] = (j + 2) ** 2 + 17


########################################
@want(
    "O00001 (test_find_flutes)                         ",
    "( mx = Var[flutes[0]]           )                 ",
    "  #101= #200                                      ",
    "( for i in flutes[1:]:          )                 ",
    "  #102= 201.                                      ",
    "N1000                                             ",
    "( for i in flutes[1:]:          )                 ",
    "  IF [#102 GE 210.] GOTO 1002                     ",
    "  #100= #[#102]                                   ",
    "(     if i > mx:                )                 ",
    "  IF [#100 LE #101] GOTO 1003                     ",
    "(         mx = i                )                 ",
    "  #101= #100                                      ",
    "  GOTO 1004                                       ",
    "N1003                                             ",
    "N1004                                             ",
    "  #102= #102 + 1.                                 ",
    "  GOTO 1000                                       ",
    "N1002                                             ",
    "  M30                                             ",
    "%                                                 ",
)
def test_find_flutes():
    i = p2g.Var()
    flutes = p2g.Fixed[10](addr=200)
    mx = p2g.Var(flutes[0])
    for i in flutes[1:]:
        if i > mx:
            mx = i


########################################
@want(
    "O00001 (test_find_max_way2)                       ",
    "( mx = Var[TOOL_TBL_FLUTES[0]]  )                 ",
    "  #100= #300                                      ",
    "( for i in TOOL_TBL_FLUTES[1:]: )                 ",
    "  #101= 301.                                      ",
    "N1000                                             ",
    "( for i in TOOL_TBL_FLUTES[1:]: )                 ",
    "  IF [#101 GE 400.] GOTO 1002                     ",
    "(     mx = max[mx, i]           )                 ",
    "  #100= #100 * [#100 GT #[#101]] + #[#101] * [#100 LE #[#101]]",
    "  #101= #101 + 1.                                 ",
    "  GOTO 1000                                       ",
    "N1002                                             ",
    "( MESSAGE.var = mx              )                 ",
    "  #3006= #100                                     ",
    "  M30                                             ",
    "%                                                 ",
)
def test_find_max_way2():
    # stop with alarm code as max # flutes in table.

    mx = p2g.Var(TOOL_TBL_FLUTES[0])
    for i in TOOL_TBL_FLUTES[1:]:
        mx = max(mx, i)

    MESSAGE.var = mx


########################################
@want(
    "O00001 (test_fixedvec0)                           ",
    "( Fixed[1, 2, 3, addr=100]      )                 ",
    "  #100= 1.                                        ",
    "  #101= 2.                                        ",
    "  #102= 3.                                        ",
    "  M30                                             ",
    "%                                                 ",
)
def test_fixedvec0():
    p2g.Fixed(1, 2, 3, addr=100)


########################################
@want(
    "O00001 (test_fixedvec1)                           ",
    "( Fixed[3][1, 2, 3, addr=100]   )                 ",
    "  #100= 1.                                        ",
    "  #101= 2.                                        ",
    "  #102= 3.                                        ",
    "  M30                                             ",
    "%                                                 ",
)
def test_fixedvec1():
    p2g.Fixed[3](1, 2, 3, addr=100)


########################################
@want(
    "O00001 (test_nested0)                             ",
    "( x[z] = y[z]                   )                 ",
    "  #[#111 + 100]= #[#111 + 110]                    ",
    "  M30                                             ",
    "%                                                 ",
)
def test_nested0():
    x = p2g.Fixed[10](addr=100)
    y = p2g.Fixed[10](addr=110)
    z = p2g.Fixed(addr=111)
    x[z] = y[z]


########################################
@want(
    "O00001 (test_nested1)                             ",
    "( x[y[z]] = y[x[z]]             )                 ",
    "  #[#[#111 + 110] + 100]= #[#[#111 + 100] + 110]  ",
    "  M30                                             ",
    "%                                                 ",
)
def test_nested1():
    x = p2g.Fixed[10](addr=100)
    y = p2g.Fixed[10](addr=110)
    z = p2g.Fixed(addr=111)
    x[y[z]] = y[x[z]]


########################################
@want(
    "O00001 (test_nested1a)                            ",
    "( x[y[z + 10]] = y[x[z] + 10]   )                 ",
    "  #[#[#111 + 120] + 100]= #[#[#111 + 100] + 120]  ",
    "  M30                                             ",
    "%                                                 ",
)
def test_nested1a():
    x = p2g.Fixed[10](addr=100)
    y = p2g.Fixed[10](addr=110)
    z = p2g.Fixed(addr=111)
    x[y[z + 10]] = y[x[z] + 10]


########################################
@want(
    "O00001 (test_nested1b)                            ",
    "  M30                                             ",
    "%                                                 ",
)
def test_nested1b():
    x = p2g.Fixed[10](addr=100)
    y = p2g.Fixed[10](addr=110)
    z = p2g.Fixed(addr=111)
    x[y[z + 10]] = x[y[z + 10]]


########################################
@want(
    "O00001 (test_nested1c)                            ",
    "( x[y[z + 10]] = x[y[z + 8]]    )                 ",
    "  #[#[#111 + 120] + 100]= #[#[#111 + 118] + 100]  ",
    "  M30                                             ",
    "%                                                 ",
)
def test_nested1c():
    x = p2g.Fixed[10](addr=100)
    y = p2g.Fixed[10](addr=110)
    z = p2g.Fixed(addr=111)
    x[y[z + 10]] = x[y[z + 8]]


########################################
@want(
    "O00001 (test_nested1d)                            ",
    "  M30                                             ",
    "%                                                 ",
)
def test_nested1d():
    x = p2g.Fixed[10](addr=100)
    y = p2g.Fixed[10](addr=110)
    z = p2g.Fixed(addr=111)
    x[y[z + 10]] = x[y[z + 10]]


########################################
@want(
    "O00001 (test_nested3)                             ",
    "( x[y[:]] = x[y[z + 10]]        )                 ",
    "  #[#110 + 100]= #[#[#111 + 120] + 100]           ",
    "  #[#111 + 100]= #[#[#111 + 120] + 100]           ",
    "  #[#112 + 100]= #[#[#111 + 120] + 100]           ",
    "  #[#113 + 100]= #[#[#111 + 120] + 100]           ",
    "  #[#114 + 100]= #[#[#111 + 120] + 100]           ",
    "  #[#115 + 100]= #[#[#111 + 120] + 100]           ",
    "  #[#116 + 100]= #[#[#111 + 120] + 100]           ",
    "  #[#117 + 100]= #[#[#111 + 120] + 100]           ",
    "  #[#118 + 100]= #[#[#111 + 120] + 100]           ",
    "  #[#119 + 100]= #[#[#111 + 120] + 100]           ",
    "  M30                                             ",
    "%                                                 ",
)
def test_nested3():
    x = p2g.Fixed[10](addr=100)
    y = p2g.Fixed[10](addr=110)
    z = p2g.Fixed(addr=111)
    x[y[:]] = x[y[z + 10]]


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
    "O00001 (test_slice_all)                           ",
    "( y[1:5:2] = x[1:7:3]           )                 ",
    "  #401= #301                                      ",
    "  #403= #304                                      ",
    "  M30                                             ",
    "%                                                 ",
)
def test_slice_all():
    x = p2g.Fixed[10](addr=300)
    y = p2g.Fixed[10](addr=400)

    y[1:5:2] = x[1:7:3]


########################################
@want(
    "O00001 (test_slice_negend)                        ",
    "( y[:] = x[:-4]                 )                 ",
    "  #400= #300                                      ",
    "  #401= #301                                      ",
    "  #402= #302                                      ",
    "  #403= #303                                      ",
    "  #404= #304                                      ",
    "  #405= #305                                      ",
    "  #406= #300                                      ",
    "  #407= #301                                      ",
    "  #408= #302                                      ",
    "  #409= #303                                      ",
    "  M30                                             ",
    "%                                                 ",
)
def test_slice_negend():
    x = p2g.Fixed[10](addr=300)
    y = p2g.Fixed[10](addr=400)

    y[:] = x[:-4]


########################################
@want(
    "O00001 (test_slice_part0)                         ",
    "( Var[j[q]]                     )                 ",
    "  #100= 1.                                        ",
    "  #101= 2.                                        ",
    "  #102= 3.                                        ",
    "  M30                                             ",
    "%                                                 ",
)
def test_slice_part0():
    j = p2g.Const(1, 2, 3, 4, 5)
    q = slice(3)
    p2g.Var(j[q])


########################################
@want(
    "O00001 (test_slice_part1)                         ",
    "( Var[j[q]]                     )                 ",
    "  #100= 3.                                        ",
    "  M30                                             ",
    "%                                                 ",
)
def test_slice_part1():
    j = p2g.Const(1, 2, 3, 4, 5)
    q = slice(2, 3)
    p2g.Var(j[q])


########################################
@want(
    "O00001 (test_slice_step0)                         ",
    "( x = Fixed[0, 1, 2, 3, 4, 5, addr=300])          ",
    "  #300= 0.                                        ",
    "  #301= 1.                                        ",
    "  #302= 2.                                        ",
    "  #303= 3.                                        ",
    "  #304= 4.                                        ",
    "  #305= 5.                                        ",
    "( y[:] = x[::2]                 )                 ",
    "  #400= #300                                      ",
    "  #401= #302                                      ",
    "  #402= #304                                      ",
    "  M30                                             ",
    "%                                                 ",
)
def test_slice_step0():
    x = p2g.Fixed(0, 1, 2, 3, 4, 5, addr=300)
    y = p2g.Fixed[3](addr=400)

    y[:] = x[::2]


########################################
@want(
    errors=[
        "test_vector.py:25:32:36:     assert not (p2g.sys.address(ptr2.x) != p2g.sys.address(st.txyz.x))",
        "Only vectors have addresses.                             ^^^^",
    ]
)
def test_var_deref_addresses():
    j = p2g.Var()

    ptr = p2g.Fixed[10](addr=300)

    for j in range(7, 10):
        ptr[j] = 12

    st = add_some_symbols()

    # show that st.txyz has address 103..
    p2g.Var(st.txyz)
    ptr1 = p2g.sys.address(st.txyz.xyz)
    p2g.Var(ptr1)
    ptr2 = st.txyz

    assert ptr1 == ptr2
    assert ptr2 == st.txyz

    assert not (p2g.sys.address(ptr2.x) != p2g.sys.address(st.txyz.x))
    assert ptr1 == st.txyz.x

    assert p2g.sys.address(st.txyz.xyz) == st.txyz

    for j in range(7, 10):
        ptr[j] = j

    for j in range(2, 7):
        ptr[j] = (j + 2) ** 2 + 17


########################################
@want(
    "O00001 (test_wacky_0)                             ",
    "( x[x.xy] = x.xy                )                 ",
    "  #[#100 + 100]= #100                             ",
    "  #[#101 + 100]= #101                             ",
    "  M30                                             ",
    "%                                                 ",
)
def test_wacky_0():
    x = p2g.Fixed[10](addr=100)
    x[x.xy] = x.xy


########################################
@want(
    "O00001 (test_wacky_1)                             ",
    "( x[x.xy] = x.x                 )                 ",
    "  #[#100 + 100]= #100                             ",
    "  #[#101 + 100]= #100                             ",
    "  M30                                             ",
    "%                                                 ",
)
def test_wacky_1():
    x = p2g.Fixed[10](addr=100)
    x[x.xy] = x.x
