'''
Tests for the fakelargefile.segment module
'''


from fakelargefile.segment import segment_types


def test_common_segment_functionality():
    for segment_type in segment_types:
        segment = segment_type.example(start=7, size=42)
        content = str(segment)
        assert len(segment) == len(content) == 42
        assert segment.start == 7
        assert segment.stop == 7 + 42
        segment.start = 3
        assert segment.start == 3
        assert segment.stop == 3 + 42


def test_common_segment_subtract_from_start():
    for segment_type in segment_types:
        segment = segment_type.example(start=3, size=42)
        content = str(segment)
        segment = (segment - segment_type.example(start=1, size=7))[0]
        assert content[5:] == str(segment)
        assert len(segment) == len(str(segment)) == 37
        assert segment.start == 1
        assert segment.stop == 1 + 37


def test_common_segment_add_before_start():
    for segment_type in segment_types:
        segment = segment_type.example(start=1, size=37)
        content = str(segment)
        segment = (segment_type.example(start=0, size=7) + segment)[1]
        assert content == str(segment)
        assert len(segment) == len(str(segment)) == 37
        assert segment.start == 8
        assert segment.stop == 8 + 37


def test_common_segment_subtract_from_end():
    for segment_type in segment_types:
        segment = segment_type.example(start=8, size=37)
        content = str(segment)
        segment = (segment - segment_type.example(start=40, size=1000000))[0]
        assert content[:-5] == str(segment)
        assert len(segment) == len(str(segment)) == 32
        assert segment.start == 8
        assert segment.stop == 8 + 32


def test_common_segment_subtract_from_middle():
    for segment_type in segment_types:
        segment = segment_type.example(start=8, size=32)
        content = str(segment)
        segments = segment - segment_type.example(start=18, size=8)
        assert len(segments) == 2
        first, last = segments
        assert content[:10] == str(first)
        assert content[18:] == str(last)
        assert len(first) == len(str(first)) == 10
        assert len(last) == len(str(last)) == 14
        assert first.start == 8
        assert first.stop == 18
        assert last.start == 18
        assert last.stop == 32


def test_common_segment_add_in_middle():
    for segment_type in segment_types:
        segment = segment_type.example(start=8, size=32)
        content = str(segment)
        to_insert = segment_type.example(start=16, size=8)
        segments = segment + to_insert
        assert len(segments) == 3
        first, middle, last = segments
        assert content[:8] == str(first)
        assert str(to_insert) == str(middle)
        assert content[8:32] == str(last)
        assert len(first) == len(str(first)) == 8
        assert len(middle) == len(str(middle)) == 8
        assert len(last) == len(str(last)) == 24
        assert first.start == 8
        assert first.stop == 16
        assert middle.start == 16
        assert middle.stop == 24
        assert last.start == 24
        assert last.stop == 48


def test_common_segment_operations_after():
    for segment_type in segment_types:
        segment = segment_type.example(start=8, size=32)
        unchanged = (segment + segment_type.example(start=32, size=3))[0]
        assert segment.start == unchanged.start
        assert segment.stop == unchanged.stop
        assert len(segment) == len(unchanged)
        assert str(segment) == str(unchanged)
        unchanged = (segment - segment_type.example(start=32, size=3))[0]
        assert segment.start == unchanged.start
        assert segment.stop == unchanged.stop
        assert len(segment) == len(unchanged)
        assert str(segment) == str(unchanged)
