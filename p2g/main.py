import collections
import datetime
import pathlib
import re
import shutil
import typing

import docopt

from p2g import err
from p2g import gbl
from p2g import VERSION
from p2g import walkfunc


DOC = """
p2g - Turn Python into G-Code.

Usage:
  p2g [options]  <srcfile> [<dstfile>]
  p2g --help [ all | topics | maint | <topic>]
  p2g --version
  p2g --location
  p2g --examples <dstdir>


#   Example:
#       p2g tram-rotary.py ~/_nc_/O{countdown}tr.nc
#        Makes an output of the form ~/_nc_/O1234tr.nc
#
#       p2g --func=thisone -
#        Read from stdin, look for the 'thisone' function and write to
#        to stdout.
#

Arguments:
  <srcfile>   Source python file. [default: stdin]
  <dstfile>   Destination G-Code file. [default: stdout]
               {countdown} in file name creates a decrementing prefix
               for the output file which makes looking for the .nc in
               a crowded directory less painful - it's at the top.
               (It's the number of seconds until midnight, so clear
               the directory once a day.)
  <topic>     [ topics | all | <topic>]
        # <topic>  Print from readme starting at topic.
        # topics   List all topics.
        # all      Print all readme.
        # maint    Print maintenance options.

Options:
     --job=<jobname>      Olabel for output code.
     --function=<fname>   Function to be compiled,
                           default is last one in source file.
     --narrow             Emit comments on their own line,
                           makes text fit more easily into
                           a narrow program window.
     --version            Print version.
     --location           Print path of running executable.
     --examples=<dstdir>  Create <dstdir>, populate with
                              examples and compile.
#
#         Examples:
#           p2g --examples showme
#             Copies the examples into ./showme and then runs
#              p2g showme/vicecenter.py showme/vicecenter.nc
#              p2g showme/checkprobe.py showme/checkprobe.nc
#
#
!
!For maintenance:
!     --emit-rtl           Write internal format to output file.
!     --break              pdb.set_trace() on error.
!     --no-version         Don't put version number in outputs.
!     --verbose=<level>    Set verbosity level [default: 0]
"""


def do_examples(outdir):

    find_examples = gbl.find_ours("vicecenter.py")
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
            str(rootname.with_suffix(".py")),
            str(rootname.with_suffix(".nc")),
        ]
        gbl.sprint(f"Running p2g {sysargs[0]} {sysargs[1]}")
        main(sysargs)


# chop readme.txt into bits given back by
# choice of section.
def do_doc(want):
    doc = gbl.find_ours("readme.txt").read_text()
    doc = doc.replace("</code>", "]").replace("<code>", "[")
    lines = doc.split("\n")
    by_section = collections.defaultdict(list)
    # a section header comes the text, not TOC, looks like:
    # the form <number>  <title>
    want = want.lower()
    section_name = ""
    for line in lines:
        got = re.match("\\d+ (.*)", line)
        if got:
            section_name = got.group(1).lower()
        by_section[section_name].append(line)
    if want == "topics":
        for section in by_section:
            print(f" {section}")
        return
    doneone = False
    for section, lines in by_section.items():
        if want == "all" or want in section:
            doneone = True
            for line in lines:
                print(line)
    if not doneone:
        print(f"{want} not found, topics:")
        for section in by_section:
            print(f" {section}")


def calculate_output_file_name(provided_filename):
    # if provided_filename is empty then output is stdout.
    if provided_filename is None:
        return "-"

    now = datetime.datetime.now()
    prev_midnight_secs = now.replace(hour=0, minute=0, second=0, microsecond=0)
    mins_since = (now - prev_midnight_secs).seconds // 60
    mins_togo = 24 * 60 - mins_since
    return provided_filename.replace("{countdown}", f"{mins_togo:04d}")


def do_gen(src_name, job_name, func_name, output_name):
    if func_name is None:
        func_name = "<last>"
    job_name = job_name if job_name else "O0001"
    output_name = calculate_output_file_name(output_name)
    src_path = pathlib.Path(src_name)
    gbl.v1print(f"src: {src_path}")
    gbl.v1print(f"fnc: {func_name}")
    gbl.v1print(f"job: {job_name}")
    gbl.v1print(f"out: {output_name}")
    try:
        res = walkfunc.compile2g(func_name, src_path, job_name=job_name)
        gbl.write_nl_lines(res, output_name)
        return 0
    except err.CompilerError as exn:
        exn.report_error(absolute_lines=True)
    return 1


def main(options: typing.Optional[list[str]] = None):
    # remove comments from source to docopt.
    parseable_opts = re.sub("\n# .*", "", DOC)
    # uncomment the maint options so they can
    # be parsed.
    parseable_opts = re.sub("\n!(.*)", "\n\\1", parseable_opts)
    opts = docopt.docopt(parseable_opts, help=False, argv=options)
    gbl.config = gbl.config._replace(
        bp_on_error=opts["--break"],
        verbose=(int(opts["--verbose"])),
        narrow_output=gbl.config.narrow_output or opts["--narrow"],
        no_version=gbl.config.no_version or opts["--no-version"],
        emit_rtl=gbl.config.emit_rtl or opts["--emit-rtl"],
    )
    res = 0

    if opts["--version"]:
        gbl.sprint(VERSION)
        return 0
    if opts["--location"]:
        gbl.sprint(f"{__file__}")
        return 0
    if opts["--help"]:
        if opts["topics"]:
            do_doc("topics")
        elif opts["all"]:
            do_doc("all")
        elif opts["maint"]:
            # just print the maint stuff.
            docstr = re.sub("\n!", "\n", re.sub("\n[^!].*", "", DOC))
            gbl.sprint(docstr)
        elif opts["<topic>"]:
            do_doc(opts["<topic>"])
        else:
            # remove comment chars from usage
            # and the maint commands too.
            docstr = DOC.strip("\n").replace("#", "")
            docstr = re.sub("\n!.*", "", docstr)
            gbl.sprint(docstr)

    elif opts["--examples"]:
        do_examples(pathlib.Path(opts["--examples"]))

    else:
        res = do_gen(
            src_name=opts["<srcfile>"],
            job_name=opts["--job"],
            func_name=opts["--function"],
            output_name=opts["<dstfile>"],
        )

    return res
