import io

# from p2g.main import main
import pathlib
import sys

import p2g

from conftest import want
from p2g.main import main


std = [
    "import p2g",
    "def testfish():",
    "      X=p2g.Fixed[1](123,addr=200)",
    "      X=p2g.Fixed[7](1,2,3,4,5,6,7,addr=300)",
]


bad = [
    "import ",
    "def testfish():",
    "      X=p2g.Fixed[1](123,addr=200)",
    "      X=p2g.Fixed[7](1,2,3,4,5,6,7,addr=300)",
]


def write_func(tmpdir: pathlib.Path, src):
    tmpfile = tmpdir / "test.py"
    tmpfile.write_text(
        "\n".join(src),
        encoding="utf-8",
    )
    return tmpfile


def test_bad_syntax(capfd, tmpdir):
    tmpfile = write_func(tmpdir, bad)

    main(["--job=O123", "--narrow", str(tmpfile), "-"])
    tmpdata = capfd.readouterr()

    assert "invalid syntax" in tmpdata.err


def test_location(capfd):
    main(["help", "location"])


def test_native_job_capfd_tmpdir_stdout(capfd, tmpdir):
    tmpfile = write_func(tmpdir, std)
    main(["--job=O123", "--narrow", str(tmpfile), "-"])
    tmpdata = capfd.readouterr()
    assert "O123" in tmpdata.out


def check_version_str(vstr):
    parts = vstr.split(".")
    assert len(parts) > 2
    assert parts[0].isdigit()


def test_native_version_capfd(capfd):
    sys.argv = ["p2g", "--version"]

    main()
    got = capfd.readouterr()
    check_version_str(got.out)


def test_native_job_tmpdir(tmpdir):
    tmpfile = write_func(tmpdir, std)
    outfile = pathlib.Path(tmpdir / "test.nc")

    main(["--job=O123", str(tmpfile), str(outfile)])
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
    main(["--examples", str(tmpdir)])
    assert (tmpdir / "vicecenter.py").exists()


def gentwinfuncs(fnname, inout):
    main(["--function=" + fnname, str(inout.srcfile), str(inout.ncfile)])

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

    main(
        [
            "--function=" + "f3",
            str(inout.srcfile),
            str(inout.ncfile),
        ],
    )
    tfun = capfd.readouterr()
    assert "No such function" in tfun.err


def test_capfd(capfd):
    sys.stdin = io.StringIO("foiio")
    main(["-"])
    tmpdata = capfd.readouterr()
    assert "foiio" in tmpdata.err


def test_native_capfd_tmpdir_stdout(capfd, tmpdir):
    tmpfile = write_func(tmpdir, std)

    main(
        [
            "--job=O123",
            str(tmpfile),
            "-",
        ]
    )
    tmpdata = capfd.readouterr()

    assert "O123" in tmpdata.out
    assert "testfish" in tmpdata.out


def test_native_logger_capfd_setup(capfd):
    main(["--version"])
    got = capfd.readouterr()
    check_version_str(got.out)


def test_native_capfd_location(capfd):
    main(["--location"])
    got = capfd.readouterr()
    assert "p2g" in got.out


# @pytest.mark.skip
# def test_typeguard_setup():
#     assert "typeguard" in sys.modules.keys()


def test_native_capfd_nf(capfd):
    assert main(["nothere.py"]) != 0
    got = capfd.readouterr()
    assert "File 'nothere.py' not found." in got.err


def test_native_capfd_help(capfd):
    main(["--help"])
    got = capfd.readouterr()
    assert "Usage" in got.out


def test_native_capfd_doc0(capfd):
    main(["--help", "all"])
    got = capfd.readouterr()
    assert "Many styli" in got.out


def test_native_capfd_doc1(capfd):
    main(["--help", "maint"])
    got = capfd.readouterr()
    assert "--break" in got.out


def test_native_doc_no_where(capfd):
    main(["--help"])
    got = capfd.readouterr()
    assert "Usage:" in got.out


def test_native_doc_no_where1(capfd):
    main(["--help", "bad"])
    got = capfd.readouterr()
    assert "bad not found" in got.out and "coordinates" in got.out


def test_native_doc_no_where2(capfd):
    main(["--help", "topics"])
    got = capfd.readouterr()
    assert "not found" not in got.out and "coordinates" in got.out


def test_logread(capfd, tmpdir):
    tmpfile = write_func(tmpdir, std)
    sys.argv = [
        "fish",
        "--verbose=34",
        str(tmpfile),
    ]

    main()
    got = capfd.readouterr()
    assert "Adding Code: M30" in got.out


# TESTS BELOW
