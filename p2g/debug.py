#! /usr/bin/env python
import contextlib
import pathlib
import sys
import typing
import tempfile

from loguru import logger

from p2g import err
from p2g import gbl
from p2g import lib
from p2g import stat

from p2g import walk
from p2g import main


sys.path.insert(0, "p2g/examples")
sys.path.insert(0, "p2g/tests")


def find_test_file(module_name):
    return (pathlib.Path(__file__).parent / "tests" / module_name).with_suffix(".py")


# testing can start app recursivly, clean up sys.argv
def run_one_test(module_name, fname, args):
    prev_argv = sys.argv
    sys.argv = []
    logger.info(f"starting test {fname}")
    if "native" in fname:
        inside = __import__(f"p2g.tests.{module_name}")
        fndef = getattr(getattr(inside.tests, module_name), fname)
        res = fndef(*args)
    else:
        res = walk.compile2g(
            func_name_arg=fname,
            srcfile_name=find_test_file(module_name),
            job_name=None,
            in_pytest=True,
            args=args,
        )

    sys.argv = prev_argv
    return res


# wrap tests with glue equivalent to pytest's fixtures.

# capwrap and tmpwrap return real context managers if
# the function name says the function needs it, and
# update the args to the callee test function.


@contextlib.contextmanager
def capwrap(fname, test_callee_arg):
    if "capfd" not in fname:
        yield
        return
    with lib.CaptureO(gbl.config.debug) as out:
        test_callee_arg.append(out)
        yield


@contextlib.contextmanager
def tmpwrap(fname, test_callee_arg):
    if "tmpdir" not in fname:
        yield
        return
    with tempfile.TemporaryDirectory() as tdir:
        dirpath = pathlib.Path(tdir)
        test_callee_arg.append(dirpath)
        yield


def wrap_one_test(module_name, fname):
    try:
        args: list[typing.Any] = []
        with capwrap(fname, args):
            with tmpwrap(fname, args):
                run_one_test(module_name, fname, args)

    except (AssertionError, TypeError):
        return "cerror" in fname

    except err.CompilerError as ass:  # no cover
        if "forcefail" in fname:
            return True

        # if all goes well, then this is never reached.
        if "cerror" in fname:
            return True
        print(ass.report_error())
        return False

    return True


@lib.g2l
def find_all_tests(module_name):
    test_file = find_test_file(module_name)
    func_names = walk.find_defined_funcs(test_file.read_text())
    for func_name in func_names:
        if func_name.startswith("test_"):
            yield func_name


def run_all_test_(module_name):
    with stat.Nest():
        funcs = find_all_tests(module_name)
        for key in funcs:
            lib.qprint("run", module_name, key)
            if not wrap_one_test(module_name, key):  # for debug
                breakpoint()


def test_null():
    main.main(None)


def runthem():
    tnames = [
        "not_pytest_nonlocal0",
        "not_pytest_nonlocal1",
        "not_pytest_nonlocal2",
        "not_pytest_return",
        "test_vars",
        "test_tuple",
        "test_vector",
        "test_for",
        "test_makestdvars",
        "test_main",  # contains capfd stuff
        "test_meta",
        "test_op",
        "test_func",
        "test_nt1",
        "test_goto",
        "test_error",
        "test_coords",
        "test_smoke",
        "test_builtins",
        "test_linenos",
        "test_basic",
        "test_edge",
        "test_expr",
        "test_interp",
        "test_str",
    ]

    for name in tnames:
        run_all_test_(name)


#    test_null()


def local_tests():
    res = walk.compile2g(
        func_name_arg="", srcfile_name="<null>", job_name="abc", in_pytest=False
    )
    lib.write_nl_lines(res, "-")


def run_test(maybe_module):
    def mtests():
        if maybe_module:  # for debug
            run_all_test_(maybe_module)
            return
        runthem()

    local_tests()
    mtests()
