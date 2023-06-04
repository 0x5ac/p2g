import sys

import p2g


# just code coverage really.
def test_tmpdir_makestdvars0(tmpdir):
    srcfile = str(tmpdir / "def.py")
    with open(srcfile, "w", encoding="utf-8") as of:
        of.writelines([" # MACHINE GEN BELOW", " # MACHINE GEN ABOVE"])

    p2g.main(
        [
            "stdvars",
            "--py=" + srcfile,
            "--dev=" + str(tmpdir / "ignore2"),
            "--txt=" + str(tmpdir / "ignore3"),
            "--org=" + str(tmpdir / "ignore4"),
        ]
    )
