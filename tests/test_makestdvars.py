import sys

from p2g.main import recur


sys.path.insert(0, "..")
sys.path.insert(0, "../..")


# just code coverage really.
def test_native_tmpdir_makestdvars0(tmpdir):
    srcfile = str(tmpdir) + "/def.py"
    with open(srcfile, "w", encoding="utf-8") as of:
        of.writelines([" # MACHINE GEN BELOW", " # MACHINE GEN ABOVE"])

    recur(
        [
            "stdvars",
            "--py=" + srcfile,
            "--dev=" + str(tmpdir / "ignore2.dev"),
            "--txt=" + str(tmpdir / "ignore3.txt"),
            "--org=" + str(tmpdir / "ignore4.org"),
        ]
    )
