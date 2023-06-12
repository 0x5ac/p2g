import pathlib
import re
import sys

import pytest

import p2g


# sys.path.insert(0, ".")
# sys.path.insert(0, "..")


def test_native_version_capfd(capfd):
    p2g.main(["--recursive", "version"])
    got = capfd.readouterr()
    assert "Version: p2g" in got.out


def write_func(test_file):
    test_file.write_text(
        "import p2g\n"
        "def test():\n"
        "      X=p2g.Fixed[1](123,addr=200)\n"
        "      X=p2g.Fixed[7](1,2,3,4,5,6,7,addr=300)\n",
        encoding="utf-8",
    )


def test_native_job_tmpdir(tmpdir):
    tmpfile = tmpdir / "test.py"
    write_func(tmpfile)
    outfile = pathlib.Path(str(tmpdir / "test.nc"))

    p2g.main(
        [
            "--recursive",
            "--job=O123",
            f"--out={str(outfile)}",
            "ngen",
            str(tmpfile),
        ]
    )
    tmpdata = outfile.read_text()
    assert "O123" in tmpdata


def make_inout(tmpdir):
    class Pair:
        def __init__(self):
            self.srcfile = tmpdir / "test.py"
            self.srcfile.write_text(
                "import p2g\n"
                "def f1(): \n"
                "  X=p2g.Fixed[1](123,addr=200)\n"
                "def f2(): \n"
                "  Y=p2g.Fixed[1](456,addr=200)\n",
                encoding="utf-8",
            )
            self.ncfile = tmpdir / "test.nc"

    return Pair()


def gentwinfuncs(fnname, inout):
    p2g.main(
        [
            "--recursive",
            "gen",
            "--function=" + fnname,
            "--out=" + str(inout.ncfile),
            str(inout.srcfile),
        ]
    )

    return inout.ncfile.read_text(encoding="utf-8").strip()


def test_native_function0_tmpdir(tmpdir):
    tfun = gentwinfuncs("f1", make_inout(tmpdir))
    assert "#200= 123." in tfun


def test_native_function1_tmpdir(tmpdir):
    tfun = gentwinfuncs("f2", make_inout(tmpdir))

    assert "#200= 456." in tfun


def test_native_function2_capfd_tmpdir(capfd, tmpdir):
    inout = make_inout(tmpdir)
    inout.ncfile = "-"

    p2g.main(
        [
            "--recursive",
            "gen",
            "--function=" + "f3",
            "--out=" + str(inout.ncfile),
            str(inout.srcfile),
        ]
    )
    tfun = capfd.readouterr()
    assert "No such function" in tfun.err


def test_native_cli_tmpdir_examples(tmpdir):
    p2g.main(["--outdir", tmpdir, "-q", "examples"])


def test_native_capfd_tmpdir_stdout(capfd, tmpdir):
    tmpfile = tmpdir / "test.py"
    write_func(tmpfile)
    p2g.main(
        [
            "--recursive",
            "gen",
            "--job=O123",
            str(tmpfile),
            f"--out=-",
        ]
    )
    tmpdata = capfd.readouterr()
    assert "O123" in tmpdata.out


def test_native_fake_capture0():
    with p2g.lib.CaptureO(0) as x:
        print("HI")
    assert x.out.startswith("HI")


def test_native_fake_capture1():
    with p2g.lib.CaptureO(0) as x:
        print("THERE", file=sys.stderr)
    assert x.err.startswith("THERE")


def test_native_fake_capture2():
    with p2g.lib.CaptureO(0) as x:
        print("HI")
        assert x.readouterr().out.startswith("HI")


def test_native_logger_capfd_setup(capfd):
    p2g.main(["--recursive", "--logfile=-", "--loglevel=INFO", "version"])
    got = capfd.readouterr()
    assert "Version:" in got.out


# @pytest.mark.skip
# def test_typeguard_setup():
#     assert "typeguard" in sys.modules.keys()


def test_native_capfd_nf(capfd):
    assert p2g.main(["gen", "nothere.py"]) != 0
    got = capfd.readouterr()
    assert "No such file or directory" in got.err
