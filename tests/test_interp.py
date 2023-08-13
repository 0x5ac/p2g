# flake8: noqa
import p2g

from conftest import want


PROBE = p2g.Fixed[3](addr=5061)
V = p2g.Fixed[10](addr=200)


def decor(fn):
    return fn


@decor
class F:
    def __init__(self):
        pass


# TESTS BELOW
########################################
@want(
    "O00001 (test_ann_assign)                          ",
    "( V[0] = fish                   )                 ",
    "  #200= 123.                                      ",
    "  M30                                             ",
    "%                                                 ",
)
def test_ann_assign():
    fish: int = 123
    V[0] = fish


########################################
@want(
    "O00001 (test_bool_op)                             ",
    "( V[0] = r                      )                 ",
    "  #200= 9.                                        ",
    "  M30                                             ",
    "%                                                 ",
)
def test_bool_op():
    r = 1 or 2 or 3
    r = 3 and 9
    V[0] = r


########################################
@want(
    "O00001 (test_break)                               ",
    "N1000                                             ",
    "( while V[0] < 10:              )                 ",
    "  IF [#200 GE 10.] GOTO 1002                      ",
    "(     V[0] += 1                 )                 ",
    "  #200= #200 + 1.                                 ",
    "  GOTO 1001                                       ",
    "(     V[1] += 9                 )                 ",
    "  #201= #201 + 9.                                 ",
    "  GOTO 1000                                       ",
    "N1001                                             ",
    "N1002                                             ",
    "( V[2] = 7                      )                 ",
    "  #202= 7.                                        ",
    "  M30                                             ",
    "%                                                 ",
)
def test_break():
    while V[0] < 10:
        V[0] += 1
        break
        V[1] += 9
    V[2] = 7


########################################
@want(
    errors=[
        "test_interp.py:9:11:16:     V[0] = dummy.v1       ",
        "module pytest has no attribute v1  ^^^^^          ",
    ]
)
def test_cerror_import():
    import pytest as dummy

    V[0] = dummy.v1


########################################
@want(
    errors=[
        "test_interp.py:8:4:41:     from pytest import undefined as dummy",
        "                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",
        "module pytest has no attribute undefined          ",
    ]
)
def test_cerror_import_from():
    from pytest import undefined as dummy

    V.xyz = undefined  # type: ignore # noqa: F821


########################################
@want(
    errors=[
        "test_interp.py:8:4:16:     try:                   ",
        "                           ^^^^^^^^^^^^           ",
        "Feature 'try' not implemented.                    ",
    ]
)
def test_cerror_tr():
    try:
        V[0] = 1
        raise SyntaxError
    except SyntaxError:
        V[0] = 2


########################################
@want(
    errors=[
        "test_interp.py:8:4:12:     try:                   ",
        "                           ^^^^^^^^               ",
        "Feature 'try' not implemented.                    ",
    ]
)
def test_cerror_try():
    try:
        if 1:
            pass
    except SyntaxError:
        pass


########################################
@want(
    errors=[
        "test_interp.py:8:9:18:     with undefined():  # type: ignore  # noqa: F821",
        "                                ^^^^^^^^^         ",
        "Name 'undefined' is not defined.                  ",
    ]
)
def test_cerror_with():
    with undefined():  # type: ignore  # noqa: F821
        V[0] = 1


########################################
@want(
    "O00001 (test_continue)                            ",
    "N1000                                             ",
    "( while V[0] < 10:              )                 ",
    "  IF [#200 GE 10.] GOTO 1002                      ",
    "(     V[0] += 1                 )                 ",
    "  #200= #200 + 1.                                 ",
    "  GOTO 1000                                       ",
    "(     V[1] += 9                 )                 ",
    "  #201= #201 + 9.                                 ",
    "  GOTO 1000                                       ",
    "N1002                                             ",
    "( V[2] = 7                      )                 ",
    "  #202= 7.                                        ",
    "  M30                                             ",
    "%                                                 ",
)
def test_continue():
    while V[0] < 10:
        V[0] += 1
        continue
        V[1] += 9
    V[2] = 7


########################################
@want(
    "O00001 (test_del)                                 ",
    "( V[0] = len[f1]                )                 ",
    "  #200= 2.                                        ",
    "( V[1] = len[f1]                )                 ",
    "  #201= 1.                                        ",
    "  M30                                             ",
    "%                                                 ",
)
def test_del():
    f1 = {"a": "b", "c": "d"}
    V[0] = len(f1)
    del f1["a"]
    V[1] = len(f1)


########################################
@want(
    "O00001 (test_delatt)                              ",
    "  M30                                             ",
    "%                                                 ",
)
def test_delatt():
    class F:
        togo = 1

    del F.togo


########################################
@want(
    "O00001 (test_dict)                                ",
    "( V[0] = r[1]                   )                 ",
    "  #200= 9.                                        ",
    "  M30                                             ",
    "%                                                 ",
)
def test_dict():
    r = {1: 9, 2: 20}
    V[0] = r[1]


########################################
@want(
    "O00001 (test_dict_comp)                           ",
    "( V[0] = len[r]                 )                 ",
    "  #200= 1.                                        ",
    "  M30                                             ",
    "%                                                 ",
)
def test_dict_comp():
    r = {x: 9 for x in [1, 2, 3] if x > 2}
    V[0] = len(r)


########################################
@want(
    "O00001 (test_ifop)                                ",
    "( V[2] = 9                      )                 ",
    "  #202= 9.                                        ",
    "( V[3] = 1                      )                 ",
    "  #203= 1.                                        ",
    "( V[0] = V[2] if V[3] else V[4] )                 ",
    "  #200= #202 * [#203 NE 0.] + #204 * [#203 EQ 0.] ",
    "  M30                                             ",
    "%                                                 ",
)
def test_ifop():
    V[2] = 9
    V[3] = 1

    V[0] = V[2] if V[3] else V[4]


########################################
@want(
    "O00001 (test_ifs)                                 ",
    "( if PROBE.x > 9:               )                 ",
    "  IF [#5061 LE 9.] GOTO 1000                      ",
    "(     if PROBE.y > 10:          )                 ",
    "  IF [#5062 LE 10.] GOTO 1002                     ",
    "(         V[0] = 3              )                 ",
    "  #200= 3.                                        ",
    "  GOTO 1003                                       ",
    "N1002                                             ",
    "N1003                                             ",
    "  GOTO 1001                                       ",
    "N1000                                             ",
    "N1001                                             ",
    "  M30                                             ",
    "%                                                 ",
)
def test_ifs():
    if PROBE.x > 9:
        if PROBE.y > 10:
            V[0] = 3


########################################
@want(
    "O00001 (test_joined_string0)                      ",
    "( V[0] = len[r]                 )                 ",
    "  #200= 6.                                        ",
    "  M30                                             ",
    "%                                                 ",
)
def test_joined_string0():
    r = "abc" + "def"
    V[0] = len(r)


########################################
@want(
    "O00001 (test_joined_string1)                      ",
    "( V[0] = len[r]                 )                 ",
    "  #200= 9.                                        ",
    "  M30                                             ",
    "%                                                 ",
)
def test_joined_string1():
    r = "abc" + f"def{123:0x}"

    V[0] = len(r)


########################################
@want(
    "O00001 (test_joined_string3)                      ",
    "( V[0] = len[r]                 )                 ",
    "  #200= 13.                                       ",
    "  M30                                             ",
    "%                                                 ",
)
def test_joined_string3():
    r = "abc" + f"def{123:7i}"

    V[0] = len(r)


########################################
@want(
    "O00001 (test_list_comp)                           ",
    "( V[0] = r                      )                 ",
    "  #200= 3.                                        ",
    "  M30                                             ",
    "%                                                 ",
)
def test_list_comp():
    r = [x for x in [1, 2, 3] if x > 2]
    V[0] = r


########################################
@want(
    "O00001 (test_nonlocal)                            ",
    "( V[0] = x                      )                 ",
    "  #200= 123.                                      ",
    "( V[1] = x                      )                 ",
    "  #201= 456.                                      ",
    "(     V[9] = x1                 )                 ",
    "  #209= 789.                                      ",
    "( V[2] = x                      )                 ",
    "  #202= 456.                                      ",
    "  M30                                             ",
    "%                                                 ",
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


########################################
@want(
    "O00001 (test_set)                                 ",
    "( V[0] = len[r]                 )                 ",
    "  #200= 3.                                        ",
    "  M30                                             ",
    "%                                                 ",
)
def test_set():
    r = {1, 2, 3}
    V[0] = len(r)


########################################
@want(
    "O00001 (test_set_comp)                            ",
    "( V[0] = r                      )                 ",
    "  #200= 3.                                        ",
    "  M30                                             ",
    "%                                                 ",
)
def test_set_comp():
    r = {x for x in [1, 2, 3] if x > 2}
    V[0] = r


########################################
@want(
    "O00001 (test_shortcut_if0)                        ",
    "(     V[1] = 12                 )                 ",
    "  #201= 12.                                       ",
    "  M30                                             ",
    "%                                                 ",
)
def test_shortcut_if0():
    if 0:
        V[0] = 7
    else:
        V[1] = 12


########################################
@want(
    "O00001 (test_shortcut_if1)                        ",
    "(     V[0] = 7                  )                 ",
    "  #200= 7.                                        ",
    "  M30                                             ",
    "%                                                 ",
)
def test_shortcut_if1():
    if 1:
        V[0] = 7
    else:
        V[1] = 12


########################################
@want(
    "O00001 (test_while)                               ",
    "N1000                                             ",
    "( while V[0] < 10:              )                 ",
    "  IF [#200 GE 10.] GOTO 1002                      ",
    "(     if V[2]:                  )                 ",
    "  IF [#202] GOTO 1001                             ",
    "(     V[0] += 1                 )                 ",
    "  #200= #200 + 1.                                 ",
    "  GOTO 1000                                       ",
    "N1002                                             ",
    "(     V[1] = 10                 )                 ",
    "  #201= 10.                                       ",
    "N1001                                             ",
    "( V[2] = 123                    )                 ",
    "  #202= 123.                                      ",
    "  M30                                             ",
    "%                                                 ",
)
def test_while():
    while V[0] < 10:
        if V[2]:
            break
        V[0] += 1
    else:
        V[1] = 10
    V[2] = 123
