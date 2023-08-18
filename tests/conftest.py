import pytest
import contextlib
import difflib
import inspect
import pathlib
import itertools
import sys

import p2g
import p2g.gbl
import p2g.err
import p2g.walkfunc
import p2g.abandon


def pytest_addoption(parser):
    # fake so that command parser doesn't get syntax error,
    # real check is in writefile.
    parser.addoption("--gif", action="store_true", default="remember callow as gold")


# the assert here will get rewritten by pytest.
def checkit(gold_txts, gold_errs, got):
    assert got[0] == gold_txts
    assert got[1] == gold_errs


def pytest_assertrepr_compare(op, left, right):
    return list(_pytest_assertrepr_compare_(op, left, right))


def _pytest_assertrepr_compare_(op, left, right):
    if op != "==":
        return None

    assert isinstance(left, list)
    assert isinstance(right, list)

    def prepend(txt, this, other):
        prev_was_blank = False
        for thisel, otherel in itertools.zip_longest(this, other, fillvalue=""):
            if not thisel:
                if prev_was_blank:
                    continue
                prev_was_blank = True
            else:
                prev_was_blank = False

            echar = "*" if thisel != otherel else "|"
            yield txt + echar + thisel

    if left != right:

        yield ""
        yield "====+" + "=" * 60
        yield from prepend("WANT", left, right)
        yield "----+" + "-" * 60
        yield from prepend("GOT ", right, left)
        yield "====+" + "=" * 60

    if False and left:
        yield "AND FOR OTHER"
        yield "want=["
        for line in left:
            yield quotecommastr(line)
        yield "]"


# takes fn, works out where it lives, where to find golden output and
# where to put test output
# test_foo.py (test_zap) will make a tests/golden/test_foo_test_zap.nc file.


def make_file_path(func) -> pathlib.Path:

    first_part = pathlib.Path(func.__code__.co_filename)
    second_part = first_part.stem + func.__name__.replace("test_", "_")
    return pathlib.Path(first_part).with_name(second_part).with_suffix(".got")


#    return pathlib.Path(func.__code__.co_filename).stem + func.__name__).with_suffix(".got")


#
# find differences between two str lists
# line where error found, and a list of *s assocaited with
# broken lines.


def writelines(fn, txt):

    path = make_file_path(fn)
    p2g.gbl.log(f"Ptest output {path}")
    path.write_text("\n".join(txt) + "\n")


# compile fn, return generated errors or text.
@p2g.gbl.g2l
def get_all_comp_outputs(fn):
    from _pytest.assertion import truncate

    truncate.DEFAULT_MAX_LINES = 9999
    truncate.DEFAULT_MAX_CHARS = 9999

    try:

        outlines = p2g.abandon.compile2g(
            fn.__name__, inspect.getsourcefile(fn), job_name="O00001"
        )
        return outlines, []
    except p2g.err.CompilerError as exn:

        errlines = exn.get_report_lines()
        return [], errlines


def read_and_trim(path):
    return [line.rstrip() for line in path.open().readlines()]


@contextlib.contextmanager
def save_config(**kwargs):
    old = p2g.gbl.config
    p2g.gbl.config = p2g.gbl.config._replace(**kwargs)
    yield
    p2g.gbl.config = old


# check golden file of fn,.
def check_golden_nodec(fn):
    def check_golden__():
        with save_config(narrow_output=False, no_id=True):

            got_std, _got_err = list(get_all_comp_outputs(fn))

            gold_path = pathlib.Path(fn.__code__.co_filename).with_suffix(".nc")
            gold_data = read_and_trim(gold_path)

            if "--gif" in sys.argv or got_std != gold_data:
                writelines(fn, got_std)
            assert gold_data == got_std

    return check_golden__


# when a test fails, create source which would
# have passed.


def quotecommastr(txt):
    quote = "'" if '"' in txt else '"'
    return quote + txt.ljust(50) + quote + ","


def make_decorated_source_seed(fn, stdgot, errgot):

    tofix = ["#" * 40, "@want("]
    for line in stdgot:
        tofix.append(quotecommastr(line))
    if p2g.gbl.config.narrow_output == False:
        tofix.append(f"narrow_output={p2g.gbl.config.narrow_output},")
    if errgot:
        tofix.append("errors=[")
        for l in errgot:
            tofix.append(quotecommastr(l))
        tofix.append("]")

    tofix.append(")\n")

    lines = inspect.getsource(fn).split("\n")

    while lines and not lines[0].startswith("def"):
        lines = lines[1:]

    return tofix + lines


# check inline gold of fn.
def want(*text, narrow_output=True, errors=[], no_id=True):
    assert isinstance(text, tuple)

    text = list(text)

    def must_be_(fn):
        def must_be__():
            _, first_line = inspect.getsourcelines(fn)
            with save_config(
                short_filenames=True,
                narrow_output=narrow_output,
                no_id=no_id,
                in_pytestwant=True,
                first_line=first_line,
            ):
                for el in text:
                    assert isinstance(el, str)

                gotstd, goterr = get_all_comp_outputs(fn)

                wantstd = list((line.rstrip() for line in text))
                wanterr = list((line.rstrip() for line in errors))

                if "--gif" in sys.argv or wantstd != gotstd:
                    got = make_decorated_source_seed(fn, gotstd, goterr)
                    writelines(fn, got)

                assert wanterr == goterr
                assert wantstd == gotstd

        return must_be__

    return must_be_


# for the badge.
def pytest_sessionfinish(session, exitstatus):
    print()
    print()
    try:
        print(f"{100 - (100.0 *session.testsfailed /       session.testscollected):0.1f}")
    except ZeroDivisionError:
        print("{session.testsfailed} {session.testscollected}")

    print()
