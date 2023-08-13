from conftest import want


@want(
    errors=[
        "test_marker.py:11:0:8: def test_need_marker():    ",
        "                       ^^^^^^^^                   ",
        "need TEST BELOW before def test_need_marker():    ",
    ]
)
def test_need_marker():
    pass


########################################
@want(
    errors=[
        "test_marker.py:7:0:8: def test_need_marker():     ",
        "                      ^^^^^^^^                    ",
        "need TEST BELOW before def test_need_marker():    ",
    ]
)
def test_need_marker():
    pass
