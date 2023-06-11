import sys

# isort: skip_file
# sys.path.insert(0, "./examples")
# ys.path.insert(0, "..")
# sys.path.insert(0, ".")
# sys.path.insert(0, "../..")
sys.path.insert(0, "./p2g/examples")
# import examples
# import examples.probecalibrate
# import examples.vicecenter
import p2g.examples.probecalibrate
import p2g.examples.vicecenter


# test two ways, from inside the test machine


test_vice_center = p2g.check_golden_nodec(p2g.examples.vicecenter.vicecenter)
test_probecalibrate = p2g.check_golden_nodec(p2g.examples.probecalibrate.probecalibrate)
