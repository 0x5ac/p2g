import pathlib

import p2g

from conftest import want


# isort:off
# make sure the testing is working.

this_path = pathlib.Path(__file__)
golden_dir = this_path.parent / "golden"


# test what happens when file is no there.
make_golden_path = golden_dir / "test_meta_test_native_transitory_golden.nc"
gold_compare_fail = golden_dir / "test_meta_test_native_gold_compare_fail.nc"
meta_decorate_seed = golden_dir / "test_meta_test_decorate_seed.decorator"
meta_decorator_path = golden_dir / "test_meta_test_native_decorate_seed.decorator"


# simple fn to output to stdout
def tolist_worker():
    p2g.Fixed(2, addr=100)


# TESTS BELOW
@want(
    "O00001 (test_simple_ok)",
    "  M30",
    "%",
)
def test_simple_ok():
    print("WORKING")
    a = 3  # noqa: F841
