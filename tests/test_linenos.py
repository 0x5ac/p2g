import p2g

from p2g.ptest import must_be


@must_be(
    "Conflicting sizes 2 and 1.",
    "p2g/tests/test_linenos.py:10:19:20:     j = p2g.Var[2](1)",
    "                                                       ^",
)
def test_cerror_no0():
    # abs 6 rel 2
    #   7       3
    #   8       4
    j = p2g.Var[2](1)


@must_be(
    "Conflicting sizes 2 and 1.",
    "p2g/tests/test_linenos.py:8:19:20:     j = p2g.Var[2](1)",
    "                                                      ^",
)
def test_cerror_no1():
    # 14
    j = p2g.Var[2](1)
