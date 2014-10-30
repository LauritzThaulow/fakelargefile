'''
Tests for the fakelargefile.segment.homogenous submodule
'''


import logging

from fakelargefile.segment import HomogenousSegment


log = logging.getLogger(__name__)


def test_HomogenousSegment():
    hs = HomogenousSegment(start=3, size=8, char="\x00")
    assert hs.start == 3
    assert hs.stop == 11
    assert hs.size == 8
    assert str(hs) == "\x00" * 8
    assert hs.index("\x00", 9, 11, end_pos=True) == 10
    assert hs.index("\x00" * 2, 9, 11, end_pos=True) == 11
    index_test_args = (
        ("ab", None, None), ("a", None, None), ("\x00", 9, 4),
        ("\x00" * 9, None, None))
    for tpl in index_test_args:
        try:
            hs.index(*tpl)
        except ValueError:
            assert True
        else:
            assert False
    try:
        HomogenousSegment(start=0, size=8, char="aa")
    except ValueError:
        assert True
    else:
        assert False
