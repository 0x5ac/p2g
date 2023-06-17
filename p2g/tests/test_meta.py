#! /usr/bin/env python

import pathlib
import re

# make sure the testing is working.
import pytest

import p2g


@p2g.must_be()
def test_simple_ok():
    print("WORKING")
    a = 3


this_path = pathlib.Path(__file__)
golden_dir = this_path.parent / "golden"


# simple fn to output to stdout
def tolist_worker():
    p2g.Fixed(2, addr=100)


# two phases 'cause fixtures don't work on interp functions.
def test_native_tolist():
    got = p2g.walk.compile2g("tolist_worker", __file__, job_name=None, in_pytest=True)

    r = "#100" in got[1]
    assert r


# # gold file is there, but broken.
# meta_make_bad_gold_path = golden_dir / "test_meta_test_native_simple_xfail1.nc"


# def make_bad_gold():
#     meta_make_bad_gold_path.write_text("fail")


# @p2g.check_golden()
# @pytest.mark.xfail()
# def test_native_simple_xfail1():
#     p2g.com("A comment")
#     CURSOR = p2g.Fixed(addr=100)
#     CURSOR.x = 9


# def test_native_check_and_remove_golden():
#     assert "A comment" in meta_make_bad_gold_path.read_text()
#     meta_make_bad_gold_path.unlink()


# test what happens when file is no there.
make_golden_path = golden_dir / "test_meta_test_native_transitory_golden.nc"


# output file not there, so test fails,
# but file is created
@p2g.check_golden()
def test_native_transitory_golden():
    CURSOR = p2g.Fixed(addr=100)
    CURSOR.x = 9


# # so can be tested here.
def test_native_golden_exists():
    assert make_golden_path.exists()
    make_golden_path.unlink()


gold_compare_fail = golden_dir / "test_meta_test_native_gold_compare_fail.nc"
# test when there is a file but its wrong.


@p2g.check_golden()
@pytest.mark.xfail
def test_native_gold_compare_fail():
    # not going to match.
    gold_compare_fail.write_text("BAD")


@p2g.must_be()
def test_cleanup():
    gold_compare_fail.unlink()


meta_decorate_seed = golden_dir / "test_meta_test_decorate_seed.decorator"


def test_native_remove_seed():
    meta_decorate_seed.unlink(missing_ok=True)
    assert not meta_decorate_seed.exists()


# the force inserts an error  in the output
# so the test fails, but generates them
# error output.

meta_decorator_path = golden_dir / "test_meta_test_native_decorate_seed.decorator"


@p2g.must_be("FORCE")
def test_native_decorate_seed():
    CURSOR = p2g.Fixed(17, addr=100)


def test_native_seed_exists():
    print("GOT ", meta_decorate_seed)
    assert meta_decorator_path.exists()
    meta_decorator_path.unlink()


@pytest.mark.xfail
def test_forcefail():
    fish = pop


#    assert False


# expected fail        test_broken()
