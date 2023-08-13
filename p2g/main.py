import collections
import datetime
import pathlib
import re
import shutil
import typing

import docopt

from p2g import err
from p2g import gbl
from p2g import walkfunc


DOC = """
p2g - Turn Python into G-Code.

Usage:
  p2g [options]  <srcfile> [<dstfile>]
  p2g help [ all | topics | maint | version | location | <topic> ]
  p2g examples <dstdir>

#   For bare p2g:
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
  <topic>      [ all | topics | maint | version | location | <topic> ]
        # all      Print all readme.
        # topics   List all topics.
        # maint    Print maintenance options.
        # version  Show version
        # location Show absdir of main
        # <topic>  Print from readme starting at topic.




Options:
     --job=<jobname>      Olabel for output code.
     --function=<fname>   Function to be compiled,
                           default is last one in source file.
     --narrow             Emit comments on their own line,
                           makes text fit more easily into
                           a narrow program window.
     --short-filenames    Emit just the lsb of filenames.
!
!For maintenance:
!     --break              pdb.set_trace() on error.
!     --no-id=             Don't put version in outputs.
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
    for job in ["vicecenter", "probecalibrate", "maxflutes"]:
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

    doc = gbl.find_ours("howto.txt").read_text()
    lines = doc.split("\n")
    by_section = collections.defaultdict(list)
    # a section header comes the text, not TOC, looks like:
    # the form <number>  <title>
    want = want.lower()
    section_name = ""
    for line in lines:
        got = re.match("^\\d+[. ]+(.*)", line)
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

        for line in exn.get_report_lines():
            gbl.eprint(line)
        return 1


def prepare_optionns(options):
    # remove comments from source to docopt.
    parseable_opts = re.sub("\n# .*", "", DOC)
    # uncomment the maint options so they can
    # be parsed.
    parseable_opts = re.sub("\n!(.*)", "\n\\1", parseable_opts)
    opts = docopt.docopt(parseable_opts, help=False, argv=options)
    gbl.config = gbl.config._replace(
        bp_on_error=opts["--break"],
        short_filenames=opts["--short-filenames"],
        verbose=(int(opts["--verbose"])),
        narrow_output=gbl.config.narrow_output or opts["--narrow"],
        no_id=gbl.config.no_id or opts["--no-id"],
    )
    return opts


def do_help_options(opts):
    if opts["<topic>"]:
        do_doc(opts["<topic>"])
    elif opts["all"]:
        do_doc("all")
    elif opts["maint"]:
        docstr = re.sub("\n!", "\n", re.sub("\n[^!].*", "", DOC))
        gbl.sprint(docstr)
    elif opts["topics"]:
        do_doc("topics")
    else:
        # remove comment chars from usage
        # and the maint commands too.
        docstr = DOC.strip("\n").replace("#", "")
        docstr = re.sub("\n!.*", "", docstr)
        gbl.sprint(docstr)


def handled_dash_options(opts):
    if opts["version"]:
        from p2g import VERSION

        gbl.sprint(VERSION)
        return 1
    if opts["location"]:
        gbl.sprint(f"{__file__}")
        return 1
    if opts["help"]:
        do_help_options(opts)
        return 1
    if opts["examples"]:
        do_examples(pathlib.Path(opts["<dstdir>"]))
        return 1
    return 0


# trick - looking at the syntax for the options,
# if a 'srcfile' is called 'help', then we pretend were called
# with --help.  So you can't compile a file called help.
def trick_help_on_cmdline(opts):

    # if srcfile matches any of the other attributes, behave
    # as if that was typed.

    if opts["<srcfile>"] == "examples":

        opts["examples"] = True
        opts["<dstdir>"] = opts["<dstfile>"] if opts["<dstfile>"] else "demo"

    elif opts["<srcfile>"] == "help":
        otherkey = opts["<dstfile>"]
        opts["help"] = True
        if otherkey in opts:
            opts[otherkey] = True
        else:
            opts["<topic>"] = otherkey


def main(options: typing.Optional[list[str]] = None):

    opts = prepare_optionns(options)

    trick_help_on_cmdline(opts)
    if handled_dash_options(opts):
        return 0

    return do_gen(
        src_name=opts["<srcfile>"],
        job_name=opts["--job"],
        func_name=opts["--function"],
        output_name=opts["<dstfile>"],
    )
