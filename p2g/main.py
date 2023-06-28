#! /usr/bin/env python
import datetime
import pathlib
import re
import shutil
import sys

import docopt

import p2g

from p2g import err
from p2g import gbl
from p2g import lib
from p2g import makestdvars
from p2g import walk


DOC = """
Turns a python program into a gcode program.

Usage:
   p2g [--function=<fname> ]
       [--job=<jobname>]
       [options] gen <srcfile> [<outfile>]
#
#       Read from python <srcfile>, emit G-Code.
#
#         Output file name may include {time} which will create a decrementing
#         prefix for the output file which makes looking for the .nc in a
#         crowded directory simpler.
#
#       Examples:
#          p2g gen foo.py ~/_nc_/{time}O001-foo.nc
#             Makes an output of the form ~/_nc_/001234O001-foo.nc
#
#          p2g gen --func=thisone -
#             Read from stdin, look for the 'thisone' function and write to
#             to stdout.
#
   p2g examples <exampledir>
#         Create <exampledir>, populate with examples and compile.
#
#         Examples:
#           p2g examples showme
#             Copies the examples into ./showme and then runs
#              p2g gen showme/vicecenter.py
#              p2g gen showme/checkprobe.py
#
   p2g doc
#         Send readme.txt to console.
#
   p2g help
#         Show complete command line help.
#
   p2g version
#         Show version.
#
   p2g location
#         Show which p2g is running.
#
#      For maintenance:
     p2g [options] stdvars [--txt=<txt>] [--dev=<dev>]
                           [--py=<py>] [--org=<org>]
#               Recreate internal files.

 Options:
  --narrow                    Narrow output; formatted to fit in the
                              narrow space of the CNC machine's program
                              display.
#
#      For maintenance:
           --no-boiler-plate  Turn of job entry and terminal M30.
           --break            Breakpoint on error.
           --debug            Enter debugging code.
           --verbose          Too much.
           --logio            Even more.


"""


def do_examples(outdir):
    find_examples = lib.find_ours("vicecenter.py")
    dst_dir = outdir.resolve()
    example_dir = find_examples.parent
    example_files = example_dir.glob("[a-z]*.py")

    outdir.mkdir(exist_ok=True, parents=True)

    for src in example_files:
        dst_name = outdir / src.name
        gbl.sprint(f"Copying {src} {dst_name}")
        shutil.copy(src, dst_name)

    for job in ["vicecenter", "probecalibrate"]:
        rootname = dst_dir / job
        sysargs = [
            "gen",
            rootname.with_suffix(".py"),
            rootname.with_suffix(".nc"),
        ]

        gbl.sprint(f"Running {sysargs[0]} {sysargs[1]} {sysargs[2]}")
        recur(sysargs)


def do_doc():
    doc = lib.find_ours("readme.txt").read_text()
    gbl.sprint(doc.replace("</code>", "]").replace("<code>", "["))


def calculate_output_file_name(provided_filename):
    # if provided_filename is empty then output is stdout.
    if provided_filename is None:
        return "-"

    now = datetime.datetime.now()
    prev_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    next_midnight = 24 * 60
    mins_togo = next_midnight - (now - prev_midnight).seconds // 60

    return provided_filename.replace("{time}", f"{mins_togo:05d}")


def do_gen(src_name, job_name, func_name, output_name):
    if func_name is None:
        func_name = "<last>"

    job_name = job_name if job_name else "O0001"

    output_name = calculate_output_file_name(output_name)
    src_path = pathlib.Path(src_name)

    gbl.log(f"src: {src_path}")
    gbl.log(f"fnc: {func_name}")
    gbl.log(f"job: {job_name}")
    gbl.log(f"output: {output_name}")
    try:
        res = walk.compile2g(func_name, src_path, job_name=job_name)
        lib.write_nl_lines(res, output_name)
        return 0
    except err.CompilerError as exn:
        exn.report_error(absolute_lines=True)
    return 1


def inner_main(options: list[str]):
    # remove comments from source to docopt.

    parseable_opts = re.sub("#.*\n", "", DOC)
    options = [str(v) for v in options]

    opts = docopt.docopt(parseable_opts, help=False, argv=options)

    gbl.config = gbl.config._replace(
        debug=opts["--debug"],
        bp_on_error=opts["--break"],
        verbose=(opts["--verbose"]),
        logio=(opts["--logio"]),
    )

    res = 0
    # find first options which are set and start with a letter - ie
    # the command - there can only be one.
    match [k for (k, v) in opts.items() if v and k[0].isalpha()]:
        case [] | ["help"]:
            gbl.sprint(DOC.strip("\n").replace("#", " "))

        case ["version"]:
            gbl.sprint(f"Version: p2g {p2g.VERSION}")

        case ["location"]:
            gbl.sprint(f"{pathlib.Path(__file__).parent}")

        case ["examples"]:
            do_examples(pathlib.Path(opts["<exampledir>"]))

        case ["stdvars"]:
            makestdvars.makestdvars(
                opts["--txt"],
                opts["--dev"],
                opts["--py"],
                opts["--org"],
            )

        case ["doc"]:
            do_doc()

        case ["gen"]:
            gbl.config = gbl.config._replace(
                narrow_output=gbl.config.narrow_output or opts["--narrow"],
                boiler_plate=gbl.config.boiler_plate and not opts["--no-boiler-plate"],
            )

            res = do_gen(
                src_name=opts["<srcfile>"],
                job_name=opts["--job"],
                func_name=opts["--function"],
                output_name=opts["<outfile>"],
            )

    return res


def main():
    with gbl.save_config(narrow_output=False):
        return inner_main(sys.argv[1:])


def recur(options: list[str]):
    with gbl.save_config(narrow_output=False, tin_test=True, boiler_plate=True):
        return inner_main(options)


def nrecur(options: list[str]):
    with gbl.save_config(narrow_output=False, tin_test=False, boiler_plate=False):
        return inner_main(options)
