import collections
import dataclasses
import datetime
import pathlib
import re
import shutil
import sys
import typing

from p2g import abandon
from p2g import err
from p2g import gbl
from p2g import VERSION


# usage printed when bad args are seen,
# lines starting with ! don't get printed unless
# help used.


@dataclasses.dataclass
class Opts:
    bp = False
    help = False
    location = False
    main = False
    narrow = False
    shortfilenames = False
    buildexamples = False
    version = False
    job = ""
    function = ""
    verbose = 0
    name1 = ""
    name2 = ""
    help_argument = ""


def build_examples(opts):
    if not opts.name1:
        raise err.CompilerError("Need destination directory.")

    outdir = pathlib.Path(opts.name1)
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


# chop howto.txt into bits given back by
# choice of section.
def show_doc(want):
    doc = gbl.find_ours("howto.txt").read_text()
    lines = doc.split("\n")

    # a section header comes from the text, don't confuse
    # with TOC, looks like <number>  <title>
    # keep dict of section names -> list of lines till next name.
    want = want.lower()
    by_section = collections.defaultdict(list)
    section_name = ""
    for line in lines:
        got = re.match("^\\d+[. ]+(.*)", line)
        if got:
            section_name = got.group(1).lower()
        if section_name:
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
    if not provided_filename or provided_filename == "-":
        return "-"

    now = datetime.datetime.now()
    prev_midnight_secs = now.replace(hour=0, minute=0, second=0, microsecond=0)
    mins_since = (now - prev_midnight_secs).seconds // 60
    mins_togo = 24 * 60 - mins_since
    return provided_filename.replace("{countdown}", f"{mins_togo:04d}")


def compile_to_gcode(opts):
    job_name = opts.job or "O00001"
    func_name = opts.function or "<last>"

    if not opts.name1:
        raise err.CompilerError("Need <src> [<dst>].")

    if not opts.name2:
        opts.name2 = "-"

    src_path = pathlib.Path(opts.name1)
    output_name = calculate_output_file_name(opts.name2)

    gbl.v1print(f"src: {src_path}")
    gbl.v1print(f"fnc: {func_name}")
    gbl.v1print(f"job: {job_name}")
    gbl.v1print(f"out: {output_name}")

    res = abandon.compile2g(func_name, src_path, job_name=job_name)
    gbl.write_nl_lines(res, output_name)


def grab_options(args):
    opts = Opts()

    def add_filename(name):
        if not opts.name1:
            opts.name1 = name
            return
        if not opts.name2:
            opts.name2 = name
            return
        raise err.CompilerError(f"Too many filenames at '{name}'.")

    for arg in args:
        if arg == "-" or "/" in arg or "." in arg:
            add_filename(arg)
            continue

        while arg.startswith("-"):
            arg = arg[1:]

        as_field = arg.replace("-", "")

        if (split := as_field.find("=")) > 0:
            name = as_field[:split]
            value = as_field[split + 1 :]
        else:
            name = as_field
            value = "1"

        if name not in Opts.__dict__:
            add_filename(name)
        else:
            setattr(opts, name, value)

    return opts


def wrappedmain(args: typing.Optional[list[str]] = None):
    if args is None:
        args = sys.argv[1:]

    if not args:
        show_doc("usage")
        return

    opts = grab_options(args)

    if opts.buildexamples:
        build_examples(opts)
        return

    if opts.version:
        gbl.sprint(VERSION)
        return

    if opts.location:
        gbl.sprint(f"{__file__}")
        return

    if opts.help:
        if not opts.name1:
            show_doc("usage")
            return
        show_doc(opts.name1)
        return

    gbl.config = gbl.config._replace(
        bp_on_error=opts.bp,
        short_filenames=opts.shortfilenames,
        verbose=int(opts.verbose),
        narrow_output=gbl.config.narrow_output or opts.narrow,
    )

    compile_to_gcode(opts)


def main(args: typing.Optional[list[str]] = None):
    try:
        wrappedmain(args)
    except err.CompilerError as exn:
        for line in exn.get_report_lines():
            gbl.eprint(line)
        return 1
    return 0
