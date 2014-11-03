'''
Tests for the fakelargefile.segment.homogenous submodule
'''


import logging

from fakelargefile.segment import RepeatingSegment


log = logging.getLogger(__name__)


def test_str():
    rs = RepeatingSegment(start=3, size=333, text="abcd")
    assert str(rs) == "abcd" * (333 // 4) + "a"


def test_index():
    rs = RepeatingSegment(start=3, size=333, text="abcd")
    assert rs.index("cdab", 3) == 5
    assert rs.index("dabcdabcd", 3) == 6
    assert rs.index("cdab", 6) == 9


def test_substring():
    rs = RepeatingSegment(start=3, size=333, text="abcd")
    assert rs.substring(5, 5 + 2 + 5 * 4 + 1) == "cd" + "abcd" * 5 + "a"
    assert rs.substring(5, 5 + 2 + 5 * 4) == "cd" + "abcd" * 5
    assert rs.substring(3, 3 + 5 * 4) == "abcd" * 5
    assert rs.substring(7, 7 + 5 * 4) == "abcd" * 5


def test_readline():
    rs = RepeatingSegment(start=3, size=333, text="abcd\nabcd")
    assert rs.readline(3) == "abcd\n"
    assert rs.readline(8) == "abcdabcd\n"
    assert rs.readline(17) == "abcdabcd\n"


def test_cut_in_middle():
    rs = RepeatingSegment(start=5, size=505, text="abcdefghij")
    last = rs.cut(start=10, stop=15)[-1]
    assert last.substring(start=15, stop=20) == "abcde"
    assert last.copy(start=10).substring(start=10, stop=15) == "abcde"

    assert rs.substring(start=39, stop=45) == "efghij"
    assert rs.substring(start=45, stop=55) == "abcdefghij"
    last = rs.cut(start=24, stop=39)[-1]
    assert last.substring(start=39, stop=45) == "efghij"
    assert last.substring(start=45, stop=55) == "abcdefghij"
    assert last.copy(start=0).substring(start=2, stop=5) == "ghi"
