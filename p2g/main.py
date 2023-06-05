#! /usr/bin/env python
import pathlib
import shutil
import sys

import docopt

from loguru import logger

from p2g import debug
from p2g import err
from p2g import gbl
from p2g import lib
from p2g import makestdvars
from p2g import version
from p2g import walk


DOC = """
Turns a python program into a gcode program.

Usage:
   p2g [options] gen <srcfile>
   p2g [options] test [<srcfile>]
   p2g [options] examples
   p2g [options] version
   p2g [options] stdvars [--txt=<txtfile>] [--dev=<devfile>] [--py=<pyfile>] [--org=<orgfile>]

Try:
   p2g gen -o ../nc/O05AC.nc vf3/vicecenter.py
       Read vicecenter.py starting at the last function in file.
       Turn into gcode in ../nc/O05AC.nc

   p2g gen --func=main vf3/probecheck.py > vf3/probecheck.nc
        Run through probecheck.py(main) and make vf3/probecheck.nc

   p2g test
        Run internal test.

   p2g examples
        Copies the examples into the current directory and then runs
        p2g  gen vicecenter.py
        p2g  gen checkprobe.py

   p2g stdvars
       Regenerate machine specific definitions.

Options:
    -o <file> --out=<file>   Output file, [default: <stdout>]
    -h --help                This.
    -v --verbose             Make verbose
    --relative-paths         Errors contain paths relative to current directory.
    --relative-lines         Errors contain linenumbers relative to start of function.
    --job=<name>             Job name, [default: O0001]
    --function=<name>        Function to compile, [default: <last function in file>]
    --debug                  Enter debugging code. [default: False]
    --recursive              Notify when called by self. [default: False]
    --logfile=<logfile>      Turn on logger.and send to <logfile> [default: <stdout>]
    --loglevel=<loglevel>    Set logger.level [default: ERROR]
    --break                  Breakpoint on error.
"""


def do_examples():
    here_dir = pathlib.Path(__file__).parent
    example_dir = here_dir / "examples"
    examples = example_dir.glob("*.py")
    for src in examples:
        # if I've left crap in directory.
        if "#" in str(src):  # no cover
            continue
        print(f"Copying {src}.")
        shutil.copy(src, ".")
    for job in ["vicecenter", "probecalibrate"]:
        print(f"Running p2g {job}.py")
        print(f"  - result in {job}.nc")
        main(["gen", job + ".py"])


def setup_logger(opt):
    loglevel = opt["--loglevel"]

    if gbl.config.debug:
        loglevel = "DEBUG"

    logfile = opt["--logfile"]
    if logfile == "<stdout>":
        logfile = sys.stdout

    logger.remove()
    logger.add(
        logfile,
        level=loglevel,
        format="{message}",
    )
    logger.info("Logging on {opt['--loglevel']} {logfile}")


def do_gen(opts):
    gbl.config.in_pytest = False

    src_name = opts["<srcfile>"]
    src_path = pathlib.Path(src_name)
    job_name = src_path.stem

    out_name = "-"

    if opts["--job"] != "<srcfilename>":
        job_name = opts["--job"]

    if opts["--function"] != "<srcfilename>":
        func_name = opts["--function"]

    if opts["--out"] != "<stdout>":
        out_name = opts["--out"]

    try:
        res = walk.compile2g(func_name, src_path, job_name=job_name, in_pytest=False)
        lib.write_nl_lines(res, out_name)
        return 0
    except err.CompilerError as exn:
        exn.report_error(absolute_lines=True)
        return 1
    except FileNotFoundError as exn:
        print(exn, file=sys.stderr)
        return 1


def main(argv=None):
    opts = docopt.docopt(DOC, argv)

    gbl.config.debug = opts["--debug"]

    setup_logger(opts)
    logger.info(argv)
    if opts["--out"] == "<stdout>":
        opts["--out"] = "-"
    if opts["--break"]:  # no cover
        gbl.config.bp_on_error = True

    gbl.config.opt_relative_paths = opts["--relative-paths"]
    gbl.config.opt_relative_lines = opts["--relative-lines"]

    if opts["version"]:
        with lib.openw(opts["--out"]) as out:
            print(f"Version: p2g {version.__version__}", file=out)

    if opts["--recursive"]:
        if isinstance(argv, list):
            argv.insert(0, "p2g")
            sys.argv = argv
        gbl.config.recursive = True

    if opts["examples"]:
        do_examples()
    elif opts["stdvars"]:
        makestdvars.makestdvars(
            opts["--txt"],
            opts["--dev"],
            opts["--py"],
            opts["--org"],
        )
    elif opts["gen"]:
        retcode = do_gen(opts)
        if not opts["--recursive"]:
            return retcode

    elif opts["test"]:  # for debug
        debug.run_test(opts["<srcfile>"])
    return 0
