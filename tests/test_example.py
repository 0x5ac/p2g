import sys
import p2g


# test two ways, from inside the test machine
sys.path.insert(0, "examples")

probecalibrate = __import__("probecalibrate")
vicecenter = __import__("vicecenter")

test_vice_center = p2g.ptest.check_golden_nodec(vicecenter.vicecenter)
test_probecalibrate = p2g.ptest.check_golden_nodec(probecalibrate.probecalibrate)
