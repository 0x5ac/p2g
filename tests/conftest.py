import sys

import pytest

import p2g.ptest


sys.path.insert(0, ".")


def pytest_configure(config):
    # register an additional marker
    config.addinivalue_line("markers", "forcefail: mark test which will always blow up")


@pytest.fixture(autouse=True)
def setup():
    p2g.ptest.init_for_pytest()
