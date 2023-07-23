import p2g

from conftest import want

# TESTS BELOW


@want(
    "(Code ?stringO00001 (test_0))",
    "(Lazy )",
    "(CommentLines )",
    "(CommentLines )",
    "(Set dst(Unop opfo#exp(Constant constant101))src(Unop opfo#exp(Constant constant200)))",
    "(If exp(Binop opfo!=exp(Unop opfo#exp(Constant constant100))exp(Constant constant0))labelrefLabel(idx=1000, used=False))",
    "(Set dst(Unop opfo#exp(Constant constant100))src(Binop opfo+exp(Unop opfo#exp(Constant constant100))exp(Constant constant9)))",
    "(Goto labelrefLabel(idx=1001, used=False))",
    "(LabelDef labeldefLabel(idx=1000, used=False))",
    "(LabelDef labeldefLabel(idx=1001, used=False))",
    "(Set dst(Unop opfo#exp(Constant constant102))src(Constant constant201))",
    "(LabelDef labeldefLabel(idx=1002, used=False))",
    "(If exp(Binop opfo>=exp(Unop opfo#exp(Constant constant102))exp(Constant constant210))labelrefLabel(idx=1004, used=False))",
    "(Set dst(Unop opfo#exp(Constant constant100))src(Unop opfo#exp(Unop opfo#exp(Constant constant102))))",
    "(If exp(Binop opfo<=exp(Unop opfo#exp(Constant constant100))exp(Unop opfo#exp(Constant constant101)))labelrefLabel(idx=1005, used=False))",
    "(Set dst(Unop opfo#exp(Constant constant101))src(Unop opfo#exp(Constant constant100)))",
    "(Goto labelrefLabel(idx=1006, used=False))",
    "(LabelDef labeldefLabel(idx=1005, used=False))",
    "(LabelDef labeldefLabel(idx=1006, used=False))",
    "(IfSet exp(Binop opfo<=exp(Unop opfo#exp(Constant constant100))exp(Constant constant3))dst(Constant constant3001)src(Constant constant100))",
    "(Set dst(Unop opfo#exp(Constant constant102))src(Binop opfo+exp(Unop opfo#exp(Constant constant102))exp(Constant constant1)))",
    "(Goto labelrefLabel(idx=1002, used=False))",
    "(LabelDef labeldefLabel(idx=1004, used=False))",
    "(Dprint )",
    "(Code ?stringM30)",
    "(Code ?string%)",
    "O00001 (test_0)",
    "( Symbol Table )",
    "",
    " ( flutes :  #200.x )",
    " ( i      :  #100.x )",
    " ( mx     :  #101.x )",
    "",
    "",
    "( Yes this is a comment )",
    "( mx = Var[flutes[0]]           )",
    "  #101= #200",
    "( if i:                         )",
    "  IF [#100 NE 0.] GOTO 1000",
    "(     i += 9                    )",
    "  #100= #100 + 9.",
    "  GOTO 1001",
    "N1000",
    "N1001",
    "( for i in flutes[1:]:          )",
    "  #102= 201.",
    "N1002",
    "( for i in flutes[1:]:          )",
    "  IF [#102 GE 210.] GOTO 1004",
    "  #100= #[#102]",
    "(     if i > mx:                )",
    "  IF [#100 LE #101] GOTO 1005",
    "(         mx = i                )",
    "  #101= #100",
    "  GOTO 1006",
    "N1005",
    "N1006",
    "(     assert i > 3              )",
    "  IF [#100 LE 3.] 3001.= 100.",
    "  #102= #102 + 1.",
    "  GOTO 1002",
    "N1004",
    "DPRNT[[#100]]",
    "  M30",
    "%",
    emit_rtl=True,
)
def test_0():

    p2g.symbol.Table.print = True
    p2g.comment("Yes this is a comment")
    i = p2g.Var()
    flutes = p2g.Fixed[10](addr=200)
    mx = p2g.Var(flutes[0])
    if i:
        i += 9
    for i in flutes[1:]:
        if i > mx:
            mx = i
        assert i > 3
    p2g.dprint(f"{i}")
