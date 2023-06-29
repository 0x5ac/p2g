import io

# from p2g.main import main
import pathlib
import sys

from p2g.main import main
from p2g.main import nrecur
from p2g.main import recur
import p2g


def write_func(tmpdir: pathlib.Path):
    tmpfile = tmpdir / "test.py"
    tmpfile.write_text(
        "import p2g\n"
        "def testfish():\n"
        "      X=p2g.Fixed[1](123,addr=200)\n"
        "      X=p2g.Fixed[7](1,2,3,4,5,6,7,addr=300)\n",
        encoding="utf-8",
    )
    return tmpfile


def test_native_job_capfd_tmpdir_stdout(capfd, tmpdir):
    tmpfile = write_func(tmpdir)
    recur(["--job=O123", "--narrow", "gen", tmpfile, "-"])
    tmpdata = capfd.readouterr()
    assert "O123" in tmpdata.out


def check_version_str(vstr):
    parts = vstr.split(".")
    assert len(parts) > 2
    assert parts[0].isdigit()


def test_native_version_capfd(capfd):
    sys.argv = ["p2g", "version"]

    main()
    got = capfd.readouterr()
    check_version_str(got.out)


def test_native_job_tmpdir(tmpdir):
    tmpfile = write_func(tmpdir)
    outfile = pathlib.Path(tmpdir / "test.nc")

    recur(["--job=O123", "--narrow", "gen", tmpfile, outfile])
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


def test_native_cli_tmpdir_examples(tmpdir):
    recur(["examples", tmpdir])
    assert (tmpdir / "vicecenter.py").exists()


def gentwinfuncs(fnname, inout):
    recur(["gen", "--function=" + fnname, inout.srcfile, inout.ncfile])

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

    nrecur(
        [
            "gen",
            "--function=" + "f3",
            inout.srcfile,
            inout.ncfile,
        ]
    )
    tfun = capfd.readouterr()
    assert "No such function" in tfun.err


def test_capfd(capfd):
    sys.stdin = io.StringIO("foiio")
    recur(["gen", "-"])
    tmpdata = capfd.readouterr()
    assert "foiio" in tmpdata.err


def test_native_capfd_tmpdir_stdout(capfd, tmpdir):
    tmpfile = write_func(tmpdir)

    recur(
        [
            "gen",
            "--job=O123",
            tmpfile,
            f"-",
        ]
    )
    tmpdata = capfd.readouterr()

    assert "O123" in tmpdata.out
    assert "testfish" in tmpdata.out


def test_native_logger_capfd_setup(capfd):
    recur(["version"])
    got = capfd.readouterr()
    check_version_str(got.out)


# @pytest.mark.skip
# def test_typeguard_setup():
#     assert "typeguard" in sys.modules.keys()


def test_native_capfd_nf(capfd):
    assert recur(["gen", "nothere.py"]) != 0
    got = capfd.readouterr()
    assert "File 'nothere.py' not found." in got.err


def test_native_capfd_help(capfd):
    recur(["help"])
    got = capfd.readouterr()
    assert "Usage" in got.out


def test_native_capfd_doc(capfd):
    recur(["doc", "all"])
    got = capfd.readouterr()
    assert "Many styli" in got.out


def test_native_doc_no_where(capfd):
    recur(["doc"])
    got = capfd.readouterr()
    assert "Usage:" in got.out


def test_logread(capfd, tmpdir):
    tmpfile = write_func(tmpdir)
    sys.argv = [
        "fish",
        "--verbose",
        "gen",
        tmpfile,
    ]

    main()
    got = capfd.readouterr()
    assert "Adding Code(_comment='', txt='M30')" in got.out


def test_location(capfd):
    sys.argv = ["somewhere"]
    recur(["location"])

    got = capfd.readouterr()
    assert "somewhere" in got.out


def test_version_bump0(capfd):
    p2g.VERSION = "1.2.3+7"
    recur(["version", "--bump=3"])
    got = capfd.readouterr()
    print(got.out)
    assert got.out == "1.2.3+8\n"


def test_version_bump1(capfd):
    p2g.VERSION = "1.2.3"
    recur(["version", "--bump=3"])
    got = capfd.readouterr()
    print(got.out)
    assert got.out == "1.2.3+1\n"
