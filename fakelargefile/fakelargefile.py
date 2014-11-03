'''
Created on Oct 25, 2014

@author: lauritz
'''


from __future__ import absolute_import, division

from bisect import bisect
from itertools import islice

from fakelargefile.errors import NoContainingSegment
from fakelargefile.segment import LiteralSegment


class FakeLargeFile(object):
    def __init__(self, segments=None):
        if segments is None:
            segments = []
        self.segments = segments
        self.segment_start = [seg.start for seg in segments]
        self.pos = 0
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
            start = self.segment_containing(self.pos)
        except NoContainingSegment:
            return iter([])
        else:
            return islice(self.segments, start, None)

    def finditer(self, string, start_pos=0, end_pos=False):
        """
        Iterate over indices of occurences of string.
        """
        pos = start_pos
        for seg in self.segment_iter(start_pos):
            while True:
                try:
                    pos = seg.index(string, pos, end_pos=end_pos)
                except ValueError:
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
            if first_affected_segment.start != segment.start:
                result = first_affected_segment.cut_at(segment.start)
                altered = [
                    result[0], segment, result[1].copy(start=segment.stop)]
            else:
                altered = [
                    segment, first_affected_segment.copy(start=segment.stop)]
            for seg in self.segments[first_affected + 1:]:
                altered.append(seg.copy(start=seg.start + segment.size))
            self.segments[first_affected:] = altered
            self.segment_start[first_affected:] = [
                seg.start for seg in altered]
            self.update_size()

    def insert_literal(self, text, start=None):
        """
        Convenience method for inserting a string at position ``start``

        If start is not given, use the current position.
        """
        if start is None:
            start = self.pos
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
            first_affected_segment = self.segments[first_affected]

        if first_affected_segment.start == start:
            before = []
        else:
            before = self.segments[first_affected].cut_at(start)[0:1]

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
                after = [segment.cut_at(stop)[-1].copy(start=start)]

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

    def readline(self):
        """
        Read up to and including the next newline character, and return it.
        """
        line = []
        for seg in self.segment_iter(self.pos):
            while True:
                line.append(seg.readline(self.pos))
                self.pos += len(line[-1])
                if "\n" in line[-1]:
                    return "".join(line)
                else:
                    break

    def deleteline(self, count=1):
        """
        Delete n lines starting from the current position.
        """
        found_newlines = 0
        pos = self.pos
        for pos in self.finditer("\n", self.pos, end_pos=True):
            found_newlines += 1
            if found_newlines == count:
                break
        deleted = self[self.pos:pos]
        self.delete(self.pos, pos)
        return deleted

    def seek(self, offset, whence=0):
        """
        Seek to a certain position in the file

        Implements the python file object seek functionality.

        It does not specify what to do if whence is not 0, 1 or 2. This method
        will raise a ValueError in that case.
        """
        if whence == 0:
            self.pos = offset
        elif whence == 1:
            self.pos += offset
        elif whence == 2:
            self.pos = self.size + offset
        else:
            raise ValueError("Valid values for whence is 0, 1 or 2.")

    def tell(self):
        """
        Return the current position in the file

        Implements the python file object tell functionality.
        """
        return self.pos

    def read(self, size):
        """
        Read up to size bytes, starting from the current position

        Behaves like file-like read methods should.
        """
        ret = self[self.pos:self.pos + size]
        self.pos = self.pos + len(ret)
        return ret

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
        twice the size of the returned string.

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
