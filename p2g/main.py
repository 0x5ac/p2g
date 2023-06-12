#! /usr/bin/env python
import contextlib
import datetime
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
   p2g [options] ngen <srcfile>
   p2g [options] test 
   p2g [options] examples
   p2g [options] version
   p2g [options] stdvars [--txt=<txtfile>] [--dev=<devfile>] [--py=<pyfile>] [--org=<orgfile>]

Try:
   p2g gen -o ../nc/O05AC.nc vf3/vicecenter.py
       Read vicecenter.py starting at the last function in file.
       Turn into gcode in ../nc/O05AC.nc

   p2g ngen -o ../nc/O05AC.nc vf3/vicecenter.py
       Same as the 'gen' command, save the output is formatted
       to fit in the narrow space in the CNC machine's program
       display.

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
    --outdir <dir>           Output directory, [default: .]
    -h --help                This.
    -q --quiet               Make less noise.
    --relative-paths         Errors contain paths relative to current directory.
    --relative-lines         Errors contain linenumbers relative to start of function.
    --job=<pattern>             Job name, [default: O0001]
    --function=<name>        Function to compile, [default: <last function in file>]
    --debug                  Enter debugging code. [default: False]
    --recursive              Notify when called by self. [default: False]
    --logfile=<logfile>      Turn on logger.and send to <logfile> [default: <stdout>]
    --loglevel=<loglevel>    Set logger.level [default: ERROR]
    --break                  Breakpoint on error.

    output pattern may include <time> which will create a decrementing
    prefix for the output file which makes looking for the .nc in a
    crowded directory simpler.

    eg  --out="~/_nc_/<time>O001-foo.nc" foo.py
    makes an output of the form ~/_nc_/001234O001-foo.nc

    Output directory is used as a prefix for out, as well as output
    for examples.
"""


def do_examples():
    here_dir = pathlib.Path(__file__).parent

    example_dir = here_dir / "examples"
    examples = example_dir.glob("[a-z]*.py")

    outdir = gbl.opts["--outdir"]
    outdir.mkdir(exist_ok=True, parents=True)

    srcnames = []
    for src in examples:
        dst_name = outdir / src.parts[-1]
        lib.qprint(f"Copying {src} {dst_name}")
        shutil.copy(src, dst_name)
        srcnames.append(dst_name)
    for job in ["vicecenter", "probecalibrate"]:
        top_name = outdir / (job + ".py")
        out_name = outdir / (job + ".nc")
        sysargs = [
            "--out",
            str(out_name),
            "gen",
            str(top_name),
        ]

        lib.qprint(f"Running {' '.join(sysargs)}")
        main(sysargs)


def setup_logger():
    loglevel = gbl.opts["--loglevel"]

    logfile = gbl.opts["--logfile"]
    if logfile == "<stdout>":
        logfile = sys.stdout

    logger.remove()
    logger.add(
        logfile,
        level=loglevel,
        format="{message}",
    )
    logger.info(f"Logging on {gbl.opts['--loglevel']} {logfile}")


def output_file_name():
    now = datetime.datetime.now()
    prev_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    next_midnight = 24 * 60
    mins_togo = next_midnight - (now - prev_midnight).seconds // 60

    out_name = "-"

    if gbl.opts["--out"] != "<stdout>":
        out_name = gbl.opts["--outdir"] / pathlib.Path(gbl.opts["--out"])

    out_name = str(out_name).replace("<time>", f"{mins_togo:05d}")
    return out_name


def do_gen():
    gbl.config.in_pytest = False

    src_name = gbl.opts["<srcfile>"]
    src_path = pathlib.Path(src_name)
    job_name = src_path.stem

    if gbl.opts["--job"] != "<srcfilename>":
        job_name = gbl.opts["--job"]

    func_name = gbl.opts["--function"]

    output_name = gbl.opts["--out"]

    logger.info(f"src: {src_path}")
    logger.info(f"fnc: {func_name}")
    logger.info(f"job: {job_name}")
    logger.info(f"output: {output_name}")
    try:
        res = walk.compile2g(func_name, src_path, job_name=job_name, in_pytest=False)
        lib.write_nl_lines(res, output_name)
        return 0
    except err.CompilerError as exn:
        exn.report_error(absolute_lines=True)
    except FileNotFoundError as exn:
        print(exn, file=sys.stderr)

    # when inside self return with no error
    # even if there was one, message is in stderr.
    if gbl.opts["--recursive"]:
        return 0
    return 1


def main(options=None):
    gbl.opts = docopt.docopt(DOC, options)

    gbl.config.debug = gbl.opts["--debug"]
    gbl.config.opt_relative_paths = gbl.opts["--relative-paths"]
    gbl.config.opt_relative_lines = gbl.opts["--relative-lines"]
    gbl.config.bp_on_error = gbl.opts["--break"]

    gbl.opts["--outdir"] = pathlib.Path(gbl.opts["--outdir"])

    setup_logger()
    logger.info(options)
    gbl.opts["--out"] = output_file_name()

    if gbl.opts["version"]:
        with lib.openw(gbl.opts["--out"]) as out:
            print(f"Version: p2g {version.__version__}", file=out)

    if gbl.opts["examples"]:
        do_examples()
    elif gbl.opts["stdvars"]:
        makestdvars.makestdvars(
            gbl.opts["--txt"],
            gbl.opts["--dev"],
            gbl.opts["--py"],
            gbl.opts["--org"],
        )
    elif gbl.opts["gen"]:
        gbl.config.opt_narrow_output = False
        return do_gen()
    elif gbl.opts["ngen"]:
        gbl.config.opt_narrow_output = True
        return do_gen()
    elif gbl.opts["test"]:
        debug.run_test(gbl.opts["<srcfile>"])
    return 0
