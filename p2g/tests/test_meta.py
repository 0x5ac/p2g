#! /usr/bin/env python

import pathlib
import re

# make sure the testing is working.
import pytest

import p2g


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


@p2g.must_be()
def test_simple_ok():
    a = 3


# gold file is there, but broken.

tmp_path = golden_dir / "test_meta_test_simple_xfail1.nc"
tmp_got_path = golden_dir / "test_meta_test_simple_xfail1.got"


@p2g.check_golden()
@pytest.mark.xfail()
def test_simple_xfail1():
    p2g.com("A comment")
    tmp_path.write_text("BAD", encoding="utf-8")
    CURSOR = p2g.Fixed(addr=100)
    CURSOR.x = 9


def test_cerror_xfail_created():
    assert tmp_got_path.exists()


# test what happens when file is no there.
make_golden_path = golden_dir / "test_meta_test_native_transitory_golden.gold"


def test_native_remove_golden():
    make_golden_path.unlink(missing_ok=True)
    assert not make_golden_path.exists()


# output file not there, so test fails,
# but file is created
@p2g.check_golden()
def test_native_transitory_golden():
    CURSOR = p2g.Fixed(addr=100)
    CURSOR.x = 9


# # so can be tested here.
def test_native_golden_exists():
    assert make_golden_path.exists()


meta_decorate_seed = golden_dir / "test_meta_test_decorate_seed.decorator"


def test_native_remove_seed():
    meta_decorate_seed.unlink(missing_ok=True)
    assert not meta_decorate_seed.exists()


# the force inserts an error  in the output
# so the test fails, but generates them
# error output.
@p2g.must_be("FORCE")
def test_native_decorate_seed():
    CURSOR = p2g.Fixed(17, addr=100)


def test_native_seed_exists():
    print("GOT ", meta_decorate_seed)
    assert meta_decorate_seed.exists()
    meta_decorate_seed.unlink()


@pytest.mark.xfail
def test_forcefail():
    fish = pop


#    assert False


# expected fail        test_broken()
