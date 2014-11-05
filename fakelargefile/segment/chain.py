'''
A chain of segment instances.
'''


from __future__ import absolute_import, division

from bisect import bisect
from itertools import islice
from collections import deque

from fakelargefile.errors import NoContainingSegment
from fakelargefile.segment import LiteralSegment


class SegmentChain(object):
    """
    A SegmentChain is a sequence of contiguous segments.

    The segments are always contiguous from the first to the last, and the
    first one always starts at 0.
    """
    def __init__(self, segments=None):
        if segments is None:
            segments = []
        self.segments = segments
        self.segment_start = [seg.start for seg in segments]
        self.update_size()

    def update_size(self):
        """
        Set the size attribute to the position after the last segment
        """
        if self.segments:
            self.size = self.segments[-1].stop
        else:
            self.size = 0

    def segment_containing(self, pos):
        """
        Return an integer i such that self.segments[i] contains pos.

        If is in in between segments, return the one starting at pos.

        If pos is at or beyond the end of the last segment, raise
        NoContainingSegment.
        """
        if pos >= self.size:
            raise NoContainingSegment()
        return bisect(self.segment_start, pos) - 1

    def segment_iter(self, pos):
        """
        Iterate over self.segments starting from segment containing pos.
        """
        try:
            start = self.segment_containing(pos)
        except NoContainingSegment:
            return iter([])
        else:
            return islice(self.segments, start, None)

    def finditer(self, string, start_pos=0, end_pos=False):
        """
        Iterate over indices of occurences of string.
        """
        pos = start_pos
        overlap_size = (len(string) - 1)
        tail = deque()
        bytes_in_tail = 0
        for seg in self.segment_iter(start_pos):
            if tail:
                left_overlap = "".join(tail)[-overlap_size:]
                right_overlap = seg.substring(
                    seg.start, min(seg.start + overlap_size, seg.stop))
                overlap_string = left_overlap + right_overlap
                overlap_pos = 0
                while True:
                    try:
                        overlap_pos = overlap_string.index(string, overlap_pos)
                    except ValueError:
                        break
                    else:
                        if end_pos:
                            overlap_pos += len(string)
                        yield overlap_pos - len(left_overlap) + seg.start
                        if not end_pos:
                            overlap_pos += len(string)
            while True:
                try:
                    pos = seg.index(string, pos, end_pos=end_pos)
                except ValueError:
                    # For when the search string may span several segments,
                    # keep a record of enough of the previous segments to
                    # search for the string.
                    overlap_start = seg.stop - overlap_size
                    if seg.start <= overlap_start:
                        tail.clear()
                        bytes_in_tail = 0
                    else:
                        overlap_start = seg.start
                    tail_tip = seg.substring(overlap_start, seg.stop)
                    tail.append(tail_tip)
                    bytes_in_tail += len(tail_tip)
                    while bytes_in_tail - len(tail[0]) > overlap_size:
                        bytes_in_tail -= len(tail.popleft())
                    pos = seg.stop
                    break
                else:
                    yield pos
                    if not end_pos:
                        pos += len(string)

    def insert(self, segment):
        """
        Insert the segment, shift following bytes to the right.
        """
        try:
            first_affected = self.segment_containing(segment.start)
        except NoContainingSegment:
            self.segments.append(segment)
            self.segment_start.append(segment.start)
            self.update_size()
        else:
            first_affected_segment = self.segments[first_affected]
            before, after = first_affected_segment.cut_at(segment.start)
            altered = []
            if before:
                altered.append(before)
            altered.append(segment)
            altered.append(after.copy(start=segment.stop))
            for seg in self.segments[first_affected + 1:]:
                altered.append(seg.copy(start=seg.start + segment.size))
            self.segments[first_affected:] = altered
            self.segment_start[first_affected:] = [
                seg.start for seg in altered]
            self.update_size()

    def insert_literal(self, start, text):
        """
        Convenience method for inserting a string at position ``start``
        """
        self.insert(LiteralSegment(start, text))

    def delete(self, start, stop):
        """
        Delete from start to stop and move what follows adjacent to start.
        """
        try:
            first_affected = self.segment_containing(start)
        except NoContainingSegment:
            return
        else:
            segment = self.segments[first_affected]
            if segment.start == start:
                before = []
            else:
                before = [segment.left_part(start)]

        try:
            last_affected = self.segment_containing(stop)
        except NoContainingSegment:
            last_affected = len(self.segments)
            after = []
        else:
            segment = self.segments[last_affected]
            if stop == segment.start:
                after = []
                last_affected -= 1
            else:
                after = [segment.right_part(stop).copy(start=start)]

        altered = before + after
        for segment in self.segments[last_affected + 1:]:
            new_start = segment.start - (stop - start)
            altered.append(segment.copy(start=new_start))
        self.segments[first_affected:] = altered
        self.segment_start[first_affected:] = [
            seg.start for seg in altered]
        self.update_size()

    def append(self, segment):
        """
        Insert a copy of segment which start where the last segment stops.
        """
        self.segments.append(segment.copy(start=self.size))
        self.segment_start.append(self.size)
        self.update_size()

    def append_literal(self, text):
        """
        Append a LiteralSegment with the given text
        """
        self.segments.append(LiteralSegment(self.size, text))
        self.segment_start.append(self.size)
        self.update_size()

    def __str__(self):
        """
        Return the entire file as a string.

        .. warning:: The returned string may be too large to fit in RAM and
        cause a MemoryError.
        """
        return "".join(str(segment) for segment in self.segments)

    def __getitem__(self, slice_):
        """
        Random access read of the file content

        The entire requested slice will be returned as a string. Keep memory
        consumption in mind! This method will consume memory equivalent to
        at least twice the size of the returned string.

        Border conditions are handled in the same way as when slicing a
        regular string.
        """
        start, stop, step = slice_.indices(self.size)
        if (stop - start) * step < 0:
            # step moves in the wrong direction
            return ""
        if step < 0:
            start, stop = stop + 1, start + 1
        ret = []
        for segment in self.segment_iter(start):
            start_index = max(start, segment.start)
            stop_index = min(stop, segment.stop)
            ret.append(segment.substring(start_index, stop_index))
            if stop_index == stop:
                break
        ret = "".join(ret)
        if step != 1:
            return ret[::step]
        else:
            return ret
