import p2g

from p2g.ptest import must_be


PROBE = p2g.Fixed[3](addr=5061)
V = p2g.Fixed[10](addr=200)


def decor(fn):
    return fn


@must_be(
    "(     V[1] = 12                 )",
    "  #201= 12.",
)
def test_shortcut_if0():
    if 0:
        V[0] = 7
    else:
        V[1] = 12


@must_be(
    "(     V[0] = 7                  )",
    "  #200= 7.",
)
def test_shortcut_if1():
    if 1:
        V[0] = 7
    else:
        V[1] = 12


@decor
class F:
    def __init__(self):
        pass


@must_be(
    "( V[0] = fish                   )",
    "  #200= 123.                  ",
)
def test_ann_assign():
    fish: int = 123
    V[0] = fish


@must_be(
    "( V[0] = r                      )",
    "  #200= 9.                    ",
)
def test_bool_op():
    r = 1 or 2 or 3
    r = 3 and 9
    V[0] = r


@must_be(
    "( while V[0] < 10:              )",
    "N1000                         ",
    "  IF [#200 GE 10.] GOTO 1002",
    "(     V[0] += 1                 )",
    "  #200= #200 + 1.             ",
    "(     break                     )",
    "  GOTO 1001                   ",
    "(     V[1] += 9                 )",
    "  #201= #201 + 9.             ",
    "  GOTO 1000",
    "N1001",
    "N1002",
    "( V[2] = 7                      )",
    "  #202= 7.                    ",
)
def test_break():
    while V[0] < 10:
        V[0] += 1
        break
        V[1] += 9
    V[2] = 7


@must_be(
    "Feature 'try' not implemented.",
    "p2g/tests/test_interp.py:7:4:16:     try:",
    "                                     ^^^^^^^^^^^^",
)
def test_cerror_tr():
    try:
        V[0] = 1
        raise SyntaxError
    except SyntaxError:
        V[0] = 2


@must_be(
    "Feature 'try' not implemented.",
    "p2g/tests/test_interp.py:7:4:12:     try:",
    "                                     ^^^^^^^^",
)
def test_cerror_try():
    try:
        if 1:
            pass
    except:
        pass


@must_be(
    "Feature 'with' not implemented.",
    "p2g/tests/test_interp.py:7:4:16:     with foo():",
    "                                     ^^^^^^^^^^^^",
)
def test_cerror_with():
    with foo():
        V[0] = 1


@must_be(
    "( while V[0] < 10:              )",
    "N1000                         ",
    "  IF [#200 GE 10.] GOTO 1002",
    "(     V[0] += 1                 )",
    "  #200= #200 + 1.             ",
    "(     continue                  )",
    "  GOTO 1000                   ",
    "(     V[1] += 9                 )",
    "  #201= #201 + 9.             ",
    "  GOTO 1000",
    "N1002",
    "( V[2] = 7                      )",
    "  #202= 7.                    ",
)
def test_continue():
    while V[0] < 10:
        V[0] += 1
        continue
        V[1] += 9
    V[2] = 7


@must_be()
def test_delatt():
    class F:
        togo = 1

    del F.togo


@must_be(
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


@must_be(
    "( V[0] = len[r]                 )",
    "  #200= 1.                    ",
)
def test_dict_comp():
    r = {x: 9 for x in [1, 2, 3] if x > 2}
    V[0] = len(r)


@must_be(
    "( V[0] = r[1]                   )",
    "  #200= 9.                    ",
)
def test_dict():
    r = {1: 9, 2: 20}
    V[0] = r[1]


@must_be(
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


@must_be(
    "( if PROBE.x > 9:               )",
    "  IF [#5061 LE 9.] GOTO 1000  ",
    "(     if PROBE.y > 10:          )",
    "  IF [#5062 LE 10.] GOTO 1002 ",
    "(         V[0] = 3              )",
    "  #200= 3.                    ",
    "  GOTO 1003",
    "N1002",
    "N1003",
    "  GOTO 1001",
    "N1000",
    "N1001",
)
def test_ifs():
    if PROBE.x > 9:
        if PROBE.y > 10:
            V[0] = 3


@must_be(
    "module pytest has no attribute v2",
    "p2g/tests/test_interp.py:7:4:34:     from pytest import v2 as dummy",
    "                                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",
)
def test_cerror_import_from():
    from pytest import v2 as dummy

    V.xyz = v2


@must_be(
    "module pytest has no attribute v1",
    "p2g/tests/test_interp.py:9:11:16:     V[0] = dummy.v1",
    "                                             ^^^^^",
)
def test_cerror_import():
    import pytest as dummy

    V[0] = dummy.v1


@must_be(
    "( V[0] = len[r]                 )",
    "  #200= 8.",
)
def test_joined_string1():
    r = "abc" + f"def{123:0x}"

    V[0] = len(r)


@must_be(
    "( V[0] = len[r]                 )",
    "  #200= 6.                    ",
)
def test_joined_string0():
    r = "abc" + "def"
    V[0] = len(r)


@must_be(
    "( V[0] = r                      )",
    "  #200= 3.                    ",
)
def test_list_comp():
    r = [x for x in [1, 2, 3] if x > 2]
    V[0] = r


@must_be(
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


@must_be(
    "( V[0] = r                      )",
    "  #200= 3.                    ",
)
def test_set_comp():
    r = {x for x in [1, 2, 3] if x > 2}
    V[0] = r


@must_be(
    "( V[0] = len[r]                 )",
    "  #200= 3.                    ",
)
def test_set():
    r = {1, 2, 3}
    V[0] = len(r)


@must_be(
    "( while V[0] < 10:              )",
    "N1000                         ",
    "  IF [#200 GE 10.] GOTO 1002",
    "(     if V[2]:                  )",
    "  IF [#202] GOTO 1001         ",
    "(     V[0] += 1                 )",
    "  #200= #200 + 1.             ",
    "  GOTO 1000",
    "N1002",
    "(     V[1] = 10                 )",
    "  #201= 10.                   ",
    "N1001",
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
