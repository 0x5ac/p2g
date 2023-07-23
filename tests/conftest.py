import contextlib
import difflib
import inspect
import pathlib


import p2g
import p2g.gbl
import p2g.walkfunc


# the assert here will get rewritten by pytest.
def checkit(gold_txts, gold_errs, got):
    assert gold_txts == got[0]
    assert gold_errs == got[1]


# makes output for failing pytests.
def sdiff(want, got):

    differ = difflib.Differ()
    yield ""
    yield ""
    WIDTH = 20

    def pad(txt):
        return txt.ljust(WIDTH)

    want = list(want)

    for lhs in want:
        if len(lhs) > WIDTH:
            WIDTH = len(lhs)

    yield pad("WANT") + "*  GOT"
    for line in differ.compare(want, got):
        marker = line[0]
        rest = pad(line[2:])

        if marker == " ":
            yield rest + "|  " + rest
        elif marker == "-":
            yield rest + "<  "
        elif marker == "+":
            yield pad("") + ">  " + rest


def pytest_assertrepr_compare(op, left, right):
    if op != "==":
        return None

    yield from sdiff(left, right)


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
        p2g.err.compiler("can't find tests")

    # generated_dir <- <somewhere>/tests/golden
    generated_dir = tests_dir / "golden"
    generated_dir.mkdir(exist_ok=True)
    #  <somewhere>/tests/golden/foo_zap.nc

    #    new_filename = func.__name__.replace("test", file_part)
    new_filename = file_part + "_" + func.__name__
    return (generated_dir / new_filename).with_suffix(new_suffix)


# find differences between two str lists
# line where error found, and a list of *s assocaited with
# broken lines.


def writelines(fn, suffix, txt):
    path = make_file_path(fn, suffix)
    p2g.gbl.log(f"Ptest output {path}")
    return path.write_text("\n".join(txt))


# compile fn, return generated errors or text.
@p2g.gbl.g2l
def get_all_comp_outputs(fn):
    try:
        outlines = p2g.walkfunc.compile2g(
            fn.__name__, inspect.getsourcefile(fn), job_name="O00001"
        )
        return outlines, []
    except p2g.err.CompilerError as exn:

        errlines = exn.error_lines(absolute_lines=False, topfn=fn)
        return [], errlines


@p2g.gbl.g2l
def read_and_trim(path):
    lines = p2g.gbl.splitnl(path.read_text())
    for line in lines:
        yield line


def check_golden_worker(fn):
    callow = list(get_all_comp_outputs(fn))

    gold_path = make_file_path(fn, ".nc")
    gold_data = list(read_and_trim(gold_path))
    writelines(fn, ".got", callow[0])
    return (gold_data, []), callow


# check golden file of fn,.
def check_golden_nodec(fn):
    def check_golden__():
        with save_config(
            tin_test=True, force_no_tintest=True, narrow_output=True, no_version=True
        ):
            callow_data = list(get_all_comp_outputs(fn))
            gold_path = make_file_path(fn, ".nc")
            gold_data = list(read_and_trim(gold_path))
            writelines(fn, ".got", callow_data[0])

            checkit(gold_data, [], callow_data)

    return check_golden__


# when a test fails, create source which would
# have passed.


def quotestr(txt):
    txt = txt.replace('"', '\\"')
    return '"' + txt + '"'


def make_decorated_source_seed(fn, callow_data):
    gcode = callow_data[0]
    errors = callow_data[1]

    tofix = ["@want("]
    for line in gcode:
        tofix.append(quotestr(line).ljust(50) + ",")
    if p2g.gbl.config.narrow_output == False:
        tofix.append(f"narrow_output={p2g.gbl.config.narrow_output},")
    if errors:
        tofix.append("errors=[")
        for l in errors:
            tofix.append(quotestr(l.ljust(50)) + ",")
        tofix.append("]")

    tofix.append(")\n")

    lines = p2g.gbl.splitnl(inspect.getsource(fn))

    while lines and not lines[0].startswith("def"):
        lines = lines[1:]

    writelines(fn, ".decorator", tofix + lines)


# check inline gold of fn.
def want(*text, narrow_output=True, errors=[], no_version=True, emit_rtl=False):
    def must_be_(fn):
        def must_be__():
            with save_config(
                tin_test=True,
                narrow_output=narrow_output,
                no_version=no_version,
                emit_rtl=emit_rtl,
            ):

                callow_data = list(get_all_comp_outputs(fn))

                make_decorated_source_seed(fn, callow_data)

                checkit(
                    list((line.rstrip() for line in text)),
                    list((line.rstrip() for line in errors)),
                    callow_data,
                )

        return must_be__

    return must_be_


@contextlib.contextmanager
def save_config(**kwargs):
    old = p2g.gbl.config
    p2g.gbl.config = p2g.gbl.config._replace(**kwargs)
    yield
    p2g.gbl.config = old
