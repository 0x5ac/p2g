import p2g

from conftest import want


# TESTS BELOW
@want(
    errors=[
        "Conflicting spaces for goto, 'r9810' and 'relative'.",
        "tests/test_goto.py:9:24:25:     p2g.goto.r9810.feed(7).relative.z_first(1, 2, 3)",
        "                                                    ^",
    ]
)
def test_cerror_9810_1():
    p2g.goto.r9810.feed(7).relative.z_first(1, 2, 3)


@want(
    errors=[
        "Probe with 9810 move is illegal.                  ",
        "tests/test_goto.py:9:47:48:     p2g.goto.r9810.feed(7).probe.z_first(1, 2, 3)",
        "                                                                           ^",
    ]
)
def test_cerror_9810_2():
    p2g.goto.r9810.feed(7).probe.z_first(1, 2, 3)


@want(
    errors=[
        "MCODE with 9810 move is illegal.                  ",
        "tests/test_goto.py:9:52:53:     p2g.goto.r9810.feed(7).mcode(\"a\").z_first(1, 2, 3)",
        "                                                                                ^",
    ]
)
def test_cerror_9810_3():
    p2g.goto.r9810.feed(7).mcode("a").z_first(1, 2, 3)


@want(
    errors=[
        "Need feed rate.                                   ",
        "tests/test_goto.py:9:28:29:     p2g.goto.work.xyz(1, 2, 3)",
        "                                                        ^",
    ]
)
def test_cerror_no_feed():
    p2g.goto.work.xyz(1, 2, 3)


@want(
    errors=[
        "Conflicting orders for goto, 'xyz' and 'z_first'. ",
        "tests/test_goto.py:9:4:7:     p2g.goto.xyz.z_first.feed(7).relative.z_first(1, 2, 3)",
        "                              ^^^                 ",
    ]
)
def test_cerror_order_3():
    p2g.goto.xyz.z_first.feed(7).relative.z_first(1, 2, 3)


@want(
    errors=[
        "'goto' needs movement order, 'all', 'z_first' or 'z_last'.",
        "tests/test_goto.py:9:36:37:     p2g.goto.feed(7).relative(1, 2, 3)",
        "                                                                ^",
    ]
)
def test_cerror_order_4():
    p2g.goto.feed(7).relative(1, 2, 3)


@want(
    errors=[
        "'goto' needs movement order, 'all', 'z_first' or 'z_last'.",
        "tests/test_goto.py:9:36:37:     p2g.goto.feed(7).relative(1, 2, 3)",
        "                                                                ^",
    ]
)
def test_cerror_order_5():
    p2g.goto.feed(7).relative(1, 2, 3)


@want(
    errors=[
        "'goto' needs one of 'relative','machine', 'work' or 'R9810'.",
        "tests/test_goto.py:9:35:36:     p2g.goto.feed(7).z_first(1, 2, 3)",
        "                                                               ^",
    ]
)
def test_cerror_space3():
    p2g.goto.feed(7).z_first(1, 2, 3)


@want(
    "O00001 (test_goto_abs)",
    "( mgoto[1, 2]                   )",
    "  G90 G01 G55 F20. x1. y2.",
    "( mgoto[1, 3]                   )",
    "  G90 G01 G55 F20. x1. y3.",
    "( xgoto[3, 4]                   )",
    "  G91 G01 G55 F20. x3. y4.",
    "",
    "( goto space=work order=2 _feed=20 probe=False mcode='' )",
    "  M30",
    "%",
)
def test_goto_abs():
    mbase = p2g.goto.feed(20).all
    mgoto = mbase.work
    mgoto(1, 2)
    mgoto(1, 3)
    xgoto = mbase.relative
    xgoto(3, 4)

    p2g.comment(mgoto)


@want(
    "O00001 (test_goto_rel)",
    "( mgoto.relative.all[1, 2]      )",
    "  G91 G01 G55 F20. x1. y2.",
    "",
    "( goto space=undefined order=1 _feed=20 probe=False mcode='' )",
    "  M30",
    "%",
)
def test_goto_rel():
    mgoto = p2g.goto.feed(20)
    mgoto.relative.all(1, 2)
    p2g.comment(mgoto)


@want(
    "O00001 (test_goto_rel_and_change)",
    "( mbase.relative[1, 2]          )",
    "  G91 G01 G55 F20. x1. y2.",
    "( mgoto[3, 4]                   )",
    "  G90 G01 G55 F20. x3. y4.",
    "  G91 G01 G55 F20. x3. y4.",
    "  M30",
    "%",
)
def test_goto_rel_and_change():
    mbase = p2g.goto.feed(20).all
    mbase.relative(1, 2)
    mgoto = mbase.work
    mgoto(3, 4)
    mgoto = mbase.relative
    mgoto(3, 4)


@want(
    "O00001 (test_order0)",
    "( goto.work.feed[12].z_first[1, 2, 3])",
    "  G90 G01 G55 F12. z3.",
    "  G90 G01 G55 F12. x1. y2.",
    "  M30",
    "%",
)
def test_order0():
    p2g.goto.work.feed(12).z_first(1, 2, 3)


@want(
    "O00001 (test_order1)",
    "( goto.z_last.feed[9].relative[1, 2, 3])",
    "  G91 G01 G55 F9. x1. y2.",
    "  G91 G01 G55 F9. z3.",
    "  M30",
    "%",
)
def test_order1():
    p2g.goto.z_last.feed(9).relative(1, 2, 3)


@want(
    "O00001 (test_order3)",
    "( goto.feed[3].work.all[1, 2, 3])",
    "  G90 G01 G55 F3. x1. y2. z3.",
    "  M30",
    "%",
)
def test_order3():
    p2g.goto.feed(3).work.all(1, 2, 3)


@want(
    "O00001 (test_order4)",
    "( goto.xyz.feed[3].work[1, 2, 3])",
    "  G90 G01 G55 F3. x1. y2. z3.",
    "  M30",
    "%",
)
def test_order4():
    p2g.goto.xyz.feed(3).work(1, 2, 3)


@want(
    "O00001 (test_probe0)",
    "( mgoto.all.probe[1, 2]         )",
    "  G90 G31 G55 M79 F20. x1. y2.",
    "  M30",
    "%",
)
def test_probe0():
    mgoto = p2g.goto.work.mcode("M79").feed(20)
    mgoto.all.probe(1, 2)


@want(
    "O00001 (test_probe1)",
    "( goto.work.feed[123].z_first[1, 2, 3])",
    "  G90 G01 G55 F123. z3.",
    "  G90 G01 G55 F123. x1. y2.",
    "  M30",
    "%",
)
def test_probe1():
    p2g.goto.work.feed(123).z_first(1, 2, 3)


@want(
    "O00001 (test_probe2)",
    "( goto.probe.relative.delay[12].feed[123].z_first[1, 2, 3])",
    "  G91 G31 G55 F123. z3.",
    "  G103 P12",
    "  G91 G31 G55 F123. x1. y2.",
    "  G103 P12",
    "  M30",
    "%",
)
def test_probe2():
    p2g.goto.probe.relative.delay(12).feed(123).z_first(1, 2, 3)


@want(
    "O00001 (test_safemove)",
    "( goto.r9810.feed[7].z_first[1, 2, 3])",
    "  G65 R9810 F7. z3.",
    "  G65 R9810 F7. x1. y2.",
    "  M30",
    "%",
)
def test_safemove():
    p2g.goto.r9810.feed(7).z_first(1, 2, 3)
