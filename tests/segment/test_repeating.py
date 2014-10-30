'''
Tests for the fakelargefile.segment.homogenous submodule
'''


import logging

from fakelargefile.segment import RepeatingSegment


log = logging.getLogger(__name__)


def test_RepeatingSegment():
    rs = RepeatingSegment(start=3, size=333, text="abcd")
    assert str(rs) == "abcd" * (333 // 4) + "a"
    assert rs.index("cdab", 3) == 5
    assert rs.index("dabcdabcd", 3) == 6
    assert rs.substring(5, 5 + 2 + 5 * 4 + 1) == "cd" + "abcd" * 5 + "a"
    assert rs.substring(5, 5 + 2 + 5 * 4) == "cd" + "abcd" * 5
    assert rs.substring(3, 3 + 5 * 4) == "abcd" * 5
    assert rs.substring(7, 7 + 5 * 4) == "abcd" * 5
