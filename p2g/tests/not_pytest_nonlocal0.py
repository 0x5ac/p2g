# can't run in pytest, can't import


def test_cerror_nonlocal8():
    nonlocal fish
    fish = 3


def test_cerror_global():
    fish = 3
    global fish


p = 7


def test_cerror_nonlocal3():
    nonlocal p
    p = 8

    def zz():
        nonlocal p
        p = 3

    zz()
