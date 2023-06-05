import sys


sys.path.insert(0, ".")


def pytest_configure(config):
    # register an additional marker
    config.addinivalue_line(
        "markers", "forcefail: mark test which will always blow up"
    )  #
