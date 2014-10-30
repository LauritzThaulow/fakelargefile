'''
Tests for the fakelargefile.segment module
'''


import logging
from mock import Mock
from fakelargefile.segment import (
    segment_types, LiteralSegment, HomogenousSegment, RepeatingSegment)


log = logging.getLogger(__name__)


def test_segment_types():
    assert set(segment_types) == set([
        LiteralSegment, HomogenousSegment, RepeatingSegment])


def test_common_segment_functionality():
    for segment_type in segment_types:
        segment = segment_type.example(start=7, size=42)
        content = str(segment)
        assert len(segment) == len(content) == 42
        assert segment.start == 7
        assert segment.stop == 7 + 42
        try:
            segment.start = 3
        except AttributeError:
            assert True
        else:
            assert False
        segment = segment.copy(start=3)
        assert segment.start == 3
        assert segment.stop == 3 + 42


def test_common_segment_str_size():
    for segment_type in segment_types:
        segment = segment_type.example(start=7, size="1k")
        assert segment.size == 1024
        segment = segment_type.example(start=3, size="0.31254M")
        assert segment.size == int(1024 * 1024 * 0.31254)
        segment = segment_type.example(start=0, size="0.003G")
        assert segment.size == int(0.003 * 1024 * 1024 * 1024)


def test_common_segment_parse_slice():
    for segment_type in segment_types:
        seg = segment_type.example(start=7, size=10)
        assert seg.parse_slice(None, None) == (7, 17)
        assert seg.parse_slice(None, 15) == (7, 15)
        assert seg.parse_slice(10, None) == (10, 17)
        assert seg.parse_slice(11, 12) == (11, 12)
        assert seg.parse_slice(7, 17) == (7, 17)
        assert seg.parse_slice(None, None, local=True) == (0, 10)
        assert seg.parse_slice(None, 15, local=True) == (0, 8)
        assert seg.parse_slice(10, None, local=True) == (3, 10)
        assert seg.parse_slice(11, 12, local=True) == (4, 5)
        assert seg.parse_slice(7, 17, local=True) == (0, 10)
        for tpl in ((6, 17), (7, 18), (15, 10)):
            try:
                seg.parse_slice(*tpl)
            except ValueError:
                assert True
            else:
                assert False


def test_common_segment_intersects():
    for segment_type in segment_types:
        log.debug(segment_type)
        segment = segment_type.example(start=3, size=10)
        assert segment.intersects(0, 1) == False
        assert segment.intersects(1, 3) == False
        assert segment.intersects(2, 4) == True
        assert segment.intersects(3, 4) == True
        assert segment.intersects(4, 6) == True
        assert segment.intersects(6, 6) == True
        assert segment.intersects(12, 13) == True
        assert segment.intersects(12, 14) == True
        assert segment.intersects(13, 14) == False
        assert segment.intersects(15, 17) == False


def test_common_segment_intersects_segment():
    for segment_type in segment_types:
        log.debug(segment_type)
        segment = segment_type.example(start=3, size=10)
        segment.intersects = Mock()
        other = Mock()
        other.start = 8
        other.stop = 13
        segment.intersects_segment(other)
        assert segment.intersects.called_once_with(start=8, stop=13)


def test_common_segment_affected_by():
    for segment_type in segment_types:
        log.debug(segment_type)
        segment = segment_type.example(start=3, size=10)
        assert segment.affected_by(14) == False
        assert segment.affected_by(13) == False
        assert segment.affected_by(12) == True
        assert segment.affected_by(4) == True
        assert segment.affected_by(3) == True
        assert segment.affected_by(2) == True


def test_common_segment_affected_by_segment():
    for segment_type in segment_types:
        log.debug(segment_type)
        segment = segment_type.example(start=3, size=10)
        segment.affected_by = Mock()
        other = Mock()
        other.start = 8
        other.stop = 13
        segment.intersects_segment(other)
        assert segment.affected_by.called_once_with(start=8)


def test_common_segment_index():
    for segment_type in segment_types:
        log.debug(segment_type)
        segment = segment_type.example(start=3, size=10)
        content = str(segment)
        assert segment.index(content[0]) == segment.start
        assert segment.index(content) == segment.start
        assert segment.index(content[3:], 6) == segment.start + 3
        assert segment.index(
            content[3:-2], 6, end_pos=True) == segment.stop - 2


def test_common_segment_subtract_from_start():
    for segment_type in segment_types:
        segment = segment_type.example(start=3, size=42)
        content = str(segment)
        result = segment.cut(start=1, stop=8)
        assert len(result) == 1
        result = result[0]
        assert content[5:] == str(result)
        assert len(result) == len(str(result)) == 37
        assert result.start == 8
        assert result.stop == 8 + 37


def test_common_segment_subtract_from_end():
    for segment_type in segment_types:
        segment = segment_type.example(start=8, size=37)
        content = str(segment)
        result = segment.cut(start=40, stop=1000000)
        assert len(result) == 1
        segment = result[0]
        assert content[:-5] == str(segment)
        assert len(segment) == len(str(segment)) == 32
        assert segment.start == 8
        assert segment.stop == 8 + 32


def test_common_segment_subtract_from_middle():
    for segment_type in segment_types:
        segment = segment_type.example(start=8, size=32)
        content = str(segment)
        result = segment.cut(start=18, stop=26)
        assert len(result) == 2
        first, last = result
        assert content[:10] == str(first)
        assert content[18:] == str(last)
        assert len(first) == len(str(first)) == 10
        assert len(last) == len(str(last)) == 14
        assert first.start == 8
        assert first.stop == 18
        assert last.start == 26
        assert last.stop == 40


def test_common_segment_subtract_disjunct():
    for segment_type in segment_types:
        segment = segment_type.example(start=8, size=32)
        for start, stop in ((1, 7), (1, 8), (40, 100), (41, 293)):
            log.debug("Trying to intersect {}->{} with {}->{}".format(
                start, stop, 8, 40))
            try:
                segment.cut(start=start, stop=stop)
            except ValueError:
                assert True
            else:
                assert False


def test_common_segment_cut_in_half():
    for segment_type in segment_types:
        segment = segment_type.example(start=8, size=32)
        content = str(segment)
        result = segment.cut(start=11, stop=11)
        assert len(result) == 2
        first, last = result
        assert str(first) == content[:3]
        assert len(first) == len(str(first)) == 3
        assert first.start == 8
        assert first.stop == 11
        assert str(last) == content[3:]
        assert len(last) == len(str(last)) == 29
        assert last.start == 11
        assert last.stop == 40


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


def test_HomogenousSegment():
    hs = HomogenousSegment(start=3, size=8, char="\x00")
    assert hs.start == 3
    assert hs.stop == 11
    assert hs.size == 8
    assert str(hs) == "\x00" * 8
    assert hs.index("\x00", 9, 11, end_pos=True) == 10


def test_RepeatingSegment():
    rs = RepeatingSegment(start=3, size=13, text="abcd")
    assert str(rs) == "abcdabcdabcda"
    assert rs.index("cdab", 3) == 5
    assert rs.index("dabcdabcd", 3) == 6
