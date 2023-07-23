import sys

from conftest import check_golden_nodec


# test two ways, from inside the test machine
sys.path.insert(0, "examples")

probecalibrate = __import__("probecalibrate")
vicecenter = __import__("vicecenter")


test_vice_center = check_golden_nodec(vicecenter.vicecenter)


test_probecalibrate = check_golden_nodec(probecalibrate.probecalibrate)


# TESTS BELOW
