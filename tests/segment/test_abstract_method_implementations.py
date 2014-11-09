'''
Test functionality common to all segment subclasses
'''

COPYING = """\
    Copyright 2014 Lauritz Vesteraas Thaulow

    This file is part of the FakeLargeFile python package.

    FakeLargeFile is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License version 3,
    as published by the Free Software Foundation.

    FakeLargeFile is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU General Affero Public License
    along with FakeLargeFile.  If not, see <http://www.gnu.org/licenses/>.
    """


import logging

from mock import Mock

from fakelargefile.segment import segment_types


log = logging.getLogger(__name__)


def test_common_segment_example():
    for segment_type in segment_types:
        segment = segment_type.example(start=7, size=42)
        assert isinstance(segment, segment_type)
        content = str(segment)
        assert len(content) == 42
        assert isinstance(content, str)


def test_immutable():
    for segment_type in segment_types:
        segment = segment_type.example(start=7, size=42)
        for attr in ("start", "stop", "size"):
            try:
                setattr(segment, attr, 3)
            except AttributeError:
                assert True
            else:
                assert False


def test_size_as_si_prefix_string():
    for segment_type in segment_types:
        segment = segment_type.example(start=7, size="1k")
        assert segment.size == 1024
        segment = segment_type.example(start=3, size="0.31254M")
        assert segment.size == int(1024 * 1024 * 0.31254)
        segment = segment_type.example(start=0, size="0.003G")
        assert segment.size == int(0.003 * 1024 * 1024 * 1024)


def test_parse_slice():
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


def test_intersects():
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
        assert segment.intersects(0, 100) == True


def test_cut_from_start():
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


def test_cut_to_end():
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


def test_cut_from_middle():
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


def test_cut_disjunct():
    for segment_type in segment_types:
        segment = segment_type.example(start=8, size=32)
        for start, stop in ((1, 7), (1, 8), (40, 100), (41, 293), (15, 12)):
            log.debug("Trying to intersect {}->{} with {}->{}".format(
                start, stop, 8, 40))
            try:
                segment.cut(start=start, stop=stop)
            except ValueError:
                assert True
            else:
                assert False


def test_cut_in_half():
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


def test_cut_at():
    for segment_type in segment_types:
        log.debug(segment_type)
        segment = segment_type.example(start=3, size=10)
        segment.left_part = Mock()
        segment.right_part = Mock()
        segment.cut_at(5)
        segment.left_part.assert_called_once_with(5)
        segment.right_part.assert_called_once_with(5)
        try:
            segment.cut_at(2)
        except ValueError:
            assert True
        else:
            assert False


def test_repr():
    for segment_type in segment_types:
        log.debug(segment_type)
        fasit = "{}(start={}, stop={})".format(segment_type.__name__, 3, 13)
        assert repr(segment_type.example(start=3, size=10)) == fasit
