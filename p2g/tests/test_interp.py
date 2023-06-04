import p2g


PROBE = p2g.Fixed[3](addr=5061)
V = p2g.Fixed[10](addr=200)


def decor(fn):
    return fn


@decor
class F:
    def __init__(self):
        pass


@p2g.must_be(
    "( V[0] = fish                   )",
    "  #200= 123.                  ",
)
def test_ann_assign():
    fish: int = 123
    V[0] = fish


@p2g.must_be(
    "( V[0] = r                      )",
    "  #200= 9.                    ",
)
def test_bool_op():
    r = 1 or 2 or 3
    r = 3 and 9
    V[0] = r


@p2g.must_be(
    "( while V[0] < 10:              )",
    "L1000                         ",
    "  IF [#200 GE 10.] GOTO 1002",
    "(     V[0] += 1                 )",
    "  #200= #200 + 1.             ",
    "(     break                     )",
    "  GOTO 1001                   ",
    "(     V[1] += 9                 )",
    "  #201= #201 + 9.             ",
    "  GOTO 1000",
    "L1001",
    "L1002",
    "( V[2] = 7                      )",
    "  #202= 7.                    ",
)
def test_break():
    while V[0] < 10:
        V[0] += 1
        break
        V[1] += 9
    V[2] = 7


@p2g.must_be(
    "Try not implemented",
    "p2g/tests/test_interp.py:7:4:16:     try:",
    "                                     ^^^^^^^^^^^^",
)
def test_comperr_tr():
    try:
        V[0] = 1
        raise SyntaxError
    except SyntaxError:
        V[0] = 2


@p2g.must_be(
    "Try not implemented",
    "p2g/tests/test_interp.py:7:4:12:     try:",
    "                                     ^^^^^^^^",
)
def test_comperr_try():
    try:
        if 1:
            pass
    except:
        pass


@p2g.must_be(
    "With not implemented",
    "p2g/tests/test_interp.py:7:4:16:     with foo():",
    "                                     ^^^^^^^^^^^^",
)
def test_comperr_with():
    with foo():
        V[0] = 1


@p2g.must_be(
    "( while V[0] < 10:              )",
    "L1000                         ",
    "  IF [#200 GE 10.] GOTO 1002",
    "(     V[0] += 1                 )",
    "  #200= #200 + 1.             ",
    "(     continue                  )",
    "  GOTO 1000                   ",
    "(     V[1] += 9                 )",
    "  #201= #201 + 9.             ",
    "  GOTO 1000",
    "L1002",
    "( V[2] = 7                      )",
    "  #202= 7.                    ",
)
def test_continue():
    while V[0] < 10:
        V[0] += 1
        continue
        V[1] += 9
    V[2] = 7


@p2g.must_be()
def test_delatt():
    class F:
        togo = 1

    del F.togo


@p2g.must_be(
    "( V[0] = len[f1]                )",
    "  #200= 2.                    ",
    "( V[1] = len[f1]                )",
    "  #201= 1.                    ",
)
def test_del():
    f1 = {"a": "b", "c": "d"}
    V[0] = len(f1)
    del f1["a"]
    V[1] = len(f1)


@p2g.must_be(
    "( V[0] = len[r]                 )",
    "  #200= 1.                    ",
)
def test_dict_comp():
    r = {x: 9 for x in [1, 2, 3] if x > 2}
    V[0] = len(r)


@p2g.must_be(
    "( V[0] = r[1]                   )",
    "  #200= 9.                    ",
)
def test_dict():
    r = {1: 9, 2: 20}
    V[0] = r[1]


@p2g.must_be(
    "Illegal iterator.",
    "p2g/tests/test_interp.py:7:20:21:     for x in [1, 2, 3]:",
    "                                                      ^",
)
def test_for1():
    for x in [1, 2, 3]:
        pass


@p2g.must_be(
    "must be simple name as destination for for",
    "p2g/tests/test_interp.py:7:25:26:     for V[0] in range(1, 9):",
    "                                                            ^",
)
def test_for():
    for V[0] in range(1, 9):
        pass
    else:
        V[1] = 10


@p2g.must_be(
    "( V[2] = 9                      )",
    "  #202= 9.                    ",
    "( V[3] = 1                      )",
    "  #203= 1.                    ",
    "                              ( V[0] = V[2] if V[3] else V[4] )",
    "  #200= #202 * [#203 NE 0.] + #204 * [#203 EQ 0.]",
)
def test_ifop():
    V[2] = 9
    V[3] = 1

    V[0] = V[2] if V[3] else V[4]


@p2g.must_be(
    "( if PROBE.x > 9:               )",
    "  IF [#5061 LE 9.] GOTO 1000  ",
    "(     if PROBE.y > 10:          )",
    "  IF [#5062 LE 10.] GOTO 1002 ",
    "(         V[0] = 3              )",
    "  #200= 3.                    ",
    "  GOTO 1003",
    "L1002",
    "L1003",
    "  GOTO 1001",
    "L1000",
    "L1001",
)
def test_ifs():
    if PROBE.x > 9:
        if PROBE.y > 10:
            V[0] = 3


@p2g.must_be(
    "module pytest has no attribute v2",
    "p2g/tests/test_interp.py:7:4:34:     from pytest import v2 as dummy",
    "                                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",
)
def test_import_from():
    from pytest import v2 as dummy

    V.xyz = v2


@p2g.must_be(
    "module pytest has no attribute v1",
    "p2g/tests/test_interp.py:9:11:16:     V[0] = dummy.v1",
    "                                             ^^^^^",
)
def test_import():
    import pytest as dummy

    V[0] = dummy.v1


@p2g.must_be(
    "( V[0] = len[r]                 )",
    "  #200= 8.",
)
def test_joined_string1():
    r = "abc" + f"def{123:0x}"

    V[0] = len(r)


@p2g.must_be(
    "( V[0] = len[r]                 )",
    "  #200= 6.                    ",
)
def test_joined_string0():
    r = "abc" + "def"
    V[0] = len(r)


@p2g.must_be(
    "( V[0] = r                      )",
    "  #200= 3.                    ",
)
def test_list_comp():
    r = [x for x in [1, 2, 3] if x > 2]
    V[0] = r


@p2g.must_be(
    "( V[0] = x                      )",
    "  #200= 123.                  ",
    "( V[1] = x                      )",
    "  #201= 456.                  ",
    "(     V[9] = x1                 )",
    "  #209= 789.                  ",
    "( V[2] = x                      )",
    "  #202= 456.                  ",
)
def test_nonlocal():
    x = 123

    def inside():
        nonlocal x
        x = 456

    def not_inside():
        x1 = 789
        V[9] = x1

    V[0] = x
    inside()
    V[1] = x
    not_inside()
    V[2] = x


@p2g.must_be(
    "( V[0] = r                      )",
    "  #200= 3.                    ",
)
def test_set_comp():
    r = {x for x in [1, 2, 3] if x > 2}
    V[0] = r


@p2g.must_be(
    "( V[0] = len[r]                 )",
    "  #200= 3.                    ",
)
def test_set():
    r = {1, 2, 3}
    V[0] = len(r)


@p2g.must_be(
    "( while V[0] < 10:              )",
    "L1000                         ",
    "  IF [#200 GE 10.] GOTO 1002",
    "(     if V[2]:                  )",
    "  IF [#202] GOTO 1001         ",
    "(     V[0] += 1                 )",
    "  #200= #200 + 1.             ",
    "  GOTO 1000",
    "L1002",
    "(     V[1] = 10                 )",
    "  #201= 10.                   ",
    "L1001",
    "( V[2] = 123                    )",
    "  #202= 123.                  ",
)
def test_while():
    while V[0] < 10:
        if V[2]:
            break
        V[0] += 1
    else:
        V[1] = 10
    V[2] = 123
