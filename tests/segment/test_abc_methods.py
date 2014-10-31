'''
Tests for the fakelargefile.segment.abc submodule
'''


import logging

from fakelargefile.segment import (
    segment_types, LiteralSegment, HomogenousSegment, RepeatingSegment)


log = logging.getLogger(__name__)


def test_segment_types():
    assert set(segment_types) == set([
        LiteralSegment, HomogenousSegment, RepeatingSegment])


def test_index_implementation():
    for segment_type in segment_types:
        log.debug(segment_type)
        segment = segment_type.example(start=3, size=10)
        content = str(segment)
        assert segment.index(content[0]) == segment.start
        assert segment.index(content) == segment.start
        assert segment.index(content[3:], 6) == segment.start + 3
        assert segment.index(
            content[3:-2], 6, end_pos=True) == segment.stop - 2
        assert segment.index("", 4, 6) == 4
        assert segment.index("", 4, 4) == 4
        last_byte = content[-1]
        not_last_byte = chr((ord(last_byte) + 1) % 256)
        try:
            segment.index(not_last_byte, 12)
        except ValueError:
            assert True
        else:
            assert False


def test_copy_implementation():
    for segment_type in segment_types:
        log.debug(segment_type)
        segment = segment_type.example(start=3, size=10)
        cp = segment.copy()
        assert cp.start == segment.start
        assert cp.stop == segment.stop
        assert cp.size == segment.size
        assert str(cp) == str(segment)
        cp = segment.copy(start=0)
        assert cp.start == 0
        assert cp.stop == 10
        assert cp.size == 10
        assert str(cp) == str(segment)


def test_substring_implementation():
    for segment_type in segment_types:
        log.debug(segment_type)
        segment = segment_type.example(start=3, size=10)
        content = str(segment)
        assert segment.substring(3, 3) == ""
        assert segment.substring(3, 10) == content[:7]
        assert segment.substring(6, 7) == content[3]
        assert segment.substring(8, 13) == content[-5:]
