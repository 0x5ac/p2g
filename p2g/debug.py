#! /usr/bin/env python

import pathlib
import sys
import tempfile

from loguru import logger

from p2g import err
from p2g import gbl
from p2g import lib
from p2g import stat
from p2g import tests
from p2g import walk


# trivial pytest faker
# sys.path.insert(0, ".")
# $sys.path.insert(0, "./tests")
# sys.path.insert(0, "..")
sys.path.insert(0, "p2g/examples")
sys.path.insert(0, "p2g/tests")


def ignore_test(key):
    if "skip" in key:
        return True
    if "fail" in key:
        return True

    return False


@lib.g2l
def find_all_tests(module_name):
    __import__("p2g.tests." + module_name)
    inside = getattr(tests, module_name)
    # look for test functions
    for key, value in inside.__dict__.items():
        if key.startswith("test_"):
            if ignore_test(key):
                continue
            yield key, value


# testing can start app recursivly, clean up sys.argv
def run_one_test(fnname, fndef, args):
    prev_argv = sys.argv
    sys.argv = []
    logger.info(f"starting test {fnname}")
    res = fndef(*args)

    sys.argv = prev_argv
    return res


def wrap_one_test__(fnname, fndef, args):
    if "tmpdir" in fnname:
        with tempfile.TemporaryDirectory() as tdir:
            args.append(pathlib.Path(tdir))
            run_one_test(fnname, fndef, args)
    else:
        run_one_test(fnname, fndef, args)


def wrap_one_test_(fnname, fndef, args):
    if "capfd" in fnname:
        with lib.CaptureO(gbl.config.debug) as streams:
            args.append(streams)
            wrap_one_test__(fnname, fndef, args)
    else:
        wrap_one_test__(fnname, fndef, args)


def wrap_one_test(fnname, fndef):
    gbl.config.debug = True

    try:
        wrap_one_test_(fnname, fndef, [])

    except (TypeError, err.CompilerError, AssertionError) as ass:
        if "asserr" in fnname:
            return True
        if "xfail" in fnname:
            return True

        print("*" * 80)
        print("*" * 80)
        print("*" * 80)
        print(f"{fnname} {ass}")
        return False
    return True


def run_all_test_(module_name):
    with stat.Nest():
        todo = find_all_tests(module_name)

        for key, decorated_fn in todo:
            # too hard for me today

            print("run", module_name, key)

            if not wrap_one_test(key, decorated_fn):
                pass
            if "forcefail" in key:
                continue
            if "golden" in key:
                continue


def runthem():
    tnames = [
        "test_for",
        "test_makestdvars",
        "test_example",
        "test_main",  # contains capfd stuff
        "test_vars",
        "test_meta",
        "test_op",
        "test_vector",
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
        "test_tuple",
    ]

    for name in tnames:
        run_all_test_(name)


def local_tests():
    gbl.config.recursive = True
    res = walk.compile2g("", "-", job_name="abc", in_pytest=False)
    lib.write_nl_lines(res, "-")
    gbl.config.recursive = False


def run_test(maybe_module):
    prev = sys.argv

    def mtests():
        sys.argv = prev
        if maybe_module:
            run_all_test_(maybe_module)
            return
        runthem()

    local_tests()
    mtests()

    sys.argv = prev
