import functools
import inspect
from loguru import logger
import itertools
import pathlib
import typing

import pytest

from p2g import err
from p2g import gbl
from p2g import lib
from p2g import walk


# takes fn, works out where it lives, where to find golden output and
# where to put test output
# test_foo.py (test_zap) will make a tests/golden/test_foo_test_zap.nc file.


def make_file_path(func, new_suffix) -> pathlib.Path:
    # this_file_path <- <somewhere>/ptest.py
    this_file_path = pathlib.Path(__file__)
    # this_file_directory <- <somewhere>/p2g
    this_file_directory = this_file_path.parent

    # file_part <- function's filename
    file_part = str(pathlib.Path(func.__code__.co_filename).stem)
    #    file_part = file_part.replace("test_", "")

    # can be in <srcdir>/tests or ../tests depending upon
    # if run installed or not. Look for testdir.

    for tests_dir in [
        this_file_directory / "tests",
        this_file_directory.parent / "tests",
    ]:
        if (tests_dir / "golden").exists():
            break
    else:  # pragma: no cover
        err.compiler("can't find tests")

    # generated_dir <- <somewhere>/tests/golden
    generated_dir = tests_dir / "golden"
    generated_dir.mkdir(exist_ok=True)
    #  <somewhere>/tests/golden/foo_zap.nc

    #    new_filename = func.__name__.replace("test", file_part)
    new_filename = file_part + "_" + func.__name__
    return (generated_dir / new_filename).with_suffix(new_suffix)


def strip_comments(txt):
    txt = txt.replace(" ", "")
    idx = txt.find("(")
    if idx >= 0:
        return txt[:idx].strip()
    return txt.strip()


# find differences between two str lists
# line where error found, and a list of *s assocaited with
# broken lines.

SAME_MARKER = " | "
DIFF_MARKER = " * "


def strip_lines_comments(block):
    for line in block:
        yield strip_comments(line)


# find differences in stuff which isn't commented.
# return a set of lines with diffs.
def find_differences(
    golden_data: typing.Sequence[str],
    callow_data: typing.Sequence[str],
    check_comments: bool,
):
    lhs_src = golden_data
    rhs_src = callow_data
    if not check_comments:
        lhs_src = strip_lines_comments(lhs_src)
        rhs_src = strip_lines_comments(rhs_src)

    diffs = set()
    # skip same stuff
    for line, (want, got) in enumerate(
        itertools.zip_longest(lhs_src, rhs_src, fillvalue="")
    ):
        if want != got:
            diffs.add(line)
    return diffs


@lib.g2l
def format_differences(marks, golden_data: list[str], callow_data: list[str]):
    fromto = slice(max(min(marks) - 4, 0), min(marks) + 10)

    lhs_width = max(len(x) for x in golden_data[fromto])

    def fmt(lhs, middle, rhs):
        return lhs.ljust(lhs_width) + middle + rhs

    yield fmt("want", "", "got")

    for idx, (lhs, rhs) in enumerate(
        itertools.zip_longest(
            golden_data[fromto],
            callow_data[fromto],
            fillvalue=" - ",
        )
    ):
        yield fmt(
            lhs,
            DIFF_MARKER if idx + fromto.start in marks else SAME_MARKER,
            rhs,
        )


def writelines(fn, suffix, txt, comment):
    path = make_file_path(fn, suffix)
    print(f"WRRTIGIN {comment} to ", path)
    logger.error(f"Ptest error, writing to {comment}")
    return path.write_text(lib.nljoin(txt))


# when a test fails, create source which would
# have passed.


def make_decorated_source_seed(fn, callow_data):
    tofix = ["@p2g.must_be("]
    for line in callow_data:
        quotechar = '"'
        if quotechar in line:
            quotechar = "'"
        if line:
            tofix.append(quotechar + line + quotechar + ",")
    tofix.append(")\n")

    lines = lib.splitnl(inspect.getsource(fn))

    while lines and not lines[0].startswith("def"):
        lines = lines[1:]

    writelines(fn, ".decorator", tofix + lines, "creating decorator")


# compile fn, return generated errors or text.
@lib.g2l
def get_all_comp_outputs(fn):
    try:
        outlines = walk.compile2g(
            fn.__name__,
            inspect.getsourcefile(fn),
            job_name=None,
            in_pytest=True,
        )
    except err.CompilerError as exn:
        outlines = exn.error_lines(absolute_lines=False, topfn=fn)
    return outlines


@lib.g2l
def read_and_trim(path):
    lines = lib.splitnl(path.read_text())
    for line in lines:
        yield line


# when called from test, exceptions are sent to output file
# as well as being passed up.


# compile code and compare output with file.


def check_must_be_worker(fn, gold_data, check_comments=False):
    callow_data = get_all_comp_outputs(fn)

    markers = find_differences(gold_data, callow_data, check_comments)

    if not markers:
        return
    etext = format_differences(markers, gold_data, callow_data)

    make_decorated_source_seed(fn, callow_data)

    if "FORCE" in gold_data[0]:
        return

    # if running in pytest then exist out gracefully for them.
    # otherwise, running in debug harness.
    if gbl.config.debug:  # for debug
        err.compiler(f"ptest error {lib.nljoin(etext)}")

    pytest.fail(lib.nljoin(etext))  # for debug


def check_golden_worker(fn, check_comments):
    callow = get_all_comp_outputs(fn)

    gold_path = make_file_path(fn, ".nc")
    if gold_path.exists():
        gold_data = read_and_trim(gold_path)

        markers = find_differences(gold_data, callow, check_comments)
        if not markers:
            return
        etext = format_differences(markers, gold_data, callow)

        writelines(fn, ".got", callow)

        # if running in pytest then exist out gracefully for them.
        # otherwise, running in debug harness.
        if gbl.config.debug:  # for debug
            for line in etext:
                print(line)
            err.compiler(f"ptest error {lib.nljoin(etext)}")

        pytest.fail(lib.nljoin(etext))

    else:
        # no source gold, make it.
        writelines(fn, ".gold", callow, "no source gold, create")


# decorator for tests, turns the node into ast and calls
# the output comparer, uses relative linenumbers in reports
# so things can be added without breaking exisiting


def check_golden(check_comments=False):
    def check_golden_(fn):
        @functools.wraps(fn)
        def check_golden__():
            check_golden_worker(fn, check_comments)

        return check_golden__

    return check_golden_


def check_golden_nodec(fn):
    @functools.wraps(fn)
    def check_golden__():
        check_golden_worker(fn, False)

    return check_golden__


def must_be(*text):
    def must_be_(fn):
        @functools.wraps(fn)
        def must_be__():
            check_must_be_worker(fn, text)

        return must_be__

    return must_be_


def must_be_cc(*text):
    def must_be_(fn):
        @functools.wraps(fn)
        def must_be__():
            check_must_be_worker(fn, text, check_comments=True)

        return must_be__

    return must_be_
