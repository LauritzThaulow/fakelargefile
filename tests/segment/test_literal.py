'''
Tests for the fakelargefile.segment.homogenous submodule
'''


import logging

from fakelargefile.segment import LiteralSegment


log = logging.getLogger(__name__)


def test_LiteralSegment():
    text = "abcdefghij"
    ls = LiteralSegment(start=17, text=text)
    assert ls.start == 17
    assert ls.text == str(ls) == text
    assert ls.size == 10
    try:
        ls.index("xyz")
    except ValueError:
        assert True
    else:
        assert False
    assert ls.readline(20) == "defghij"
    ls = LiteralSegment(start=4, text="as\ndf\ngh\n")
    lines = ls.readlines(5)
    log.debug(lines)
    assert lines == ["s\n", "df\n", "gh\n"]
