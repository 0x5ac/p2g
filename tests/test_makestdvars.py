from tools import makestdvars


# just for code coverage


def test_native_tmpdir_makestdvars0(tmpdir, capfd):
    srcfile = str(tmpdir) + "/def.py"
    with open(srcfile, "w", encoding="utf-8") as of:
        of.writelines([" # MACHINE GEN BELOW", " # MACHINE GEN ABOVE"])

    makestdvars.main(
        [
            "--py=" + srcfile,
            "--dev=" + str(tmpdir / "ignore2.dev"),
            "--txt=" + str(tmpdir / "ignore3.txt"),
            "--org=" + str(tmpdir / "ignore4.org"),
        ]
    )
