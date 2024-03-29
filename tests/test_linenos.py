import p2g

from conftest import want


# TESTS BELOW
########################################
@want(
    errors=[
        "test_linenos.py:10:15:16:     p2g.Var[2](1)       ",
        "Conflicting sizes 2 and 1.               ^        ",
    ]
)
def test_cerror_no0():
    # abs 6 rel 2
    #   7       3
    #   8       4
    p2g.Var[2](1)


########################################
@want(
    errors=[
        "test_linenos.py:8:15:16:     p2g.Var[2](1)        ",
        "Conflicting sizes 2 and 1.              ^         ",
    ]
)
def test_cerror_no1():
    # 14
    p2g.Var[2](1)
