import p2g


@p2g.must_be(
    "Need feed rate.",
    "p2g/tests/test_goto.py:7:24:25:     p2g.goto.work(1, 2, 3)",
    "                                                        ^",
)
def test_cerror_no_feed():
    p2g.goto.work(1, 2, 3)


@p2g.must_be(
    "( m.relative[1, 2]              )",
    "  G01 G91 F20. x1. y2.        ",
    "( GotoWorker[want_bp_=False, space_=<MovementSpace.WORK: 1>, feed_=20, order_=<MovementOrder.XYZ: 1>, probe_=False, mcode_=''] )",
)
def test_goto_rel():
    mgoto = p2g.goto.feed(20)
    mgoto.relative(1, 2)
    p2g.comment(mgoto)


@p2g.must_be(
    "( p2.feed[12].z_then_xy[1, 2, 3])",
    "  G01 G90 F12. z3.            ",
    "  G01 G90 F12. x1. y2.",
)
def test_order0():
    p2g.goto.feed(12).z_then_xy(1, 2, 3)


@p2g.must_be(
    "( p2.xy_then_z.feed[9].relative[1, 2, 3])",
    "  G01 G91 F9. x1. y2.         ",
    "  G01 G91 F9. z3.",
)
def test_order1():
    p2g.goto.xy_then_z.feed(9).relative(1, 2, 3)


@p2g.must_be(
    "( p2.feed[3].work[1, 2, 3]      )",
    "  G01 G90 F3. x1. y2. z3.     ",
)
def test_order3():
    p2g.goto.feed(3).work(1, 2, 3)


@p2g.must_be(
    "( p2.xyz.feed[3].work[1, 2, 3]  )",
    "  G01 G90 F3. x1. y2. z3.     ",
)
def test_order4():
    p2g.goto.xyz.feed(3).work(1, 2, 3)


@p2g.must_be(
    "( m.probe[1, 2]                 )",
    "  G01 G90 G31 M79 F20. x1. y2.",
)
def test_probe0():
    mgoto = p2g.goto.mcode("M79").feed(20)
    mgoto.probe(1, 2)


@p2g.must_be(
    "( p2.feed[123].z_then_xy[1, 2, 3])",
    "  G01 G90 F123. z3.           ",
    "  G01 G90 F123. x1. y2.",
)
def test_probe1():
    p2g.goto.feed(123).z_then_xy(1, 2, 3)


@p2g.must_be(
    "( goto.r9810.feed[7].z_then_xy[1, 2, 3])",
    "  G01 G65 R9810 F7. z3.",
    "  G01 G65 R9810 F7. x1. y2.",
)
def test_safemove():
    p2g.goto.r9810.feed(7).z_then_xy(1, 2, 3)
