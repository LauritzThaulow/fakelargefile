'''
Created on Oct 25, 2014

@author: lauritz
'''


from __future__ import absolute_import, division

from bisect import bisect_left
from itertools import islice

from fakelargefile.errors import NoContainingSegment


class FakeLargeFile(object):
    def __init__(self, segments=None):
        if segments is None:
            segments = []
        self.segments = segments
        self.segment_start = [seg.start for seg in segments]
        self.pos = 0

    def segment_containing(self, pos):
        """
        Return an integer i such that self.segments[i] contains pos.

        If is in in between segments, return the one starting at pos.

        If pos is at the end of the last segment, return len(self.segments).
        """
        index = bisect_left(self.segment_start, self.pos)
        if index == 0:
            # Special case for when self.pos == 0.
            return 0
        elif index == len(self.segments):
            raise NoContainingSegment()
        else:
            return index - 1

    def current_segment_iter(self):
        """
        Return an iterator over self.segments starting from the current one.

        The current one is the one which contains or starts with self.pos.
        """
        return islice(self.segments, self.segment_containing(self.pos), None)

    def insert(self, segment):
        """
        Insert the segment, shift following bytes to the right.
        """
        try:
            first_affected = self.segment_containing(segment.start)
        except NoContainingSegment:
            self.segments.append(segment)
            self.segment_start.append(segment.start)
        else:
            result = self.segments[first_affected].cut_at(segment.start)
            altered = [result[0], segment, result[1].copy(start=segment.stop)]
            for seg in self.segments[first_affected + 1:]:
                altered.append(seg.copy(start=seg.start + segment.size))
            self.segments[first_affected:] = altered
            self.segment_start[first_affected:] = [
                seg.start for seg in altered]

    def delete(self, start, stop):
        """
        Delete from start to stop and move what follows adjacent to start.
        """
        try:
            first_affected = self.segment_containing(start)
        except NoContainingSegment:
            return
        before = self.segments[first_affected].cut_at(start)[0:0]
        try:
            last_affected = self.segment_containing(stop)
        except NoContainingSegment:
            last_affected = len(self.segments)
            after = []
        else:
            after = self.segments[last_affected].cut_at(stop)[-1:-1].copy(
                start=start)
        altered = before + after
        for segment in self.segments[last_affected + 1:]:
            altered.append(segment.copy(start=segment.start - (stop - start)))
        self.segments[first_affected:] = altered
        self.segment_start[first_affected:] = [
            seg.start for seg in altered]

    def append(self, segment):
        """
        Insert a copy of segment which start where the last segment stops.
        """
        if self.segments:
            last_segment_stop = self.segments[-1].stop
        else:
            last_segment_stop = 0
        self.segments.append(segment.copy(start=last_segment_stop))
        self.segment_start.append(last_segment_stop)

    def readline(self):
        """
        Read up to and including the next newline character, and return it.
        """
        line = []
        for seg in self.current_segment_iter():
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
        for seg in self.current_segment_iter():
            if found_newlines < count:
                break
            try:
                pos = seg.index("\n", pos, end_pos=True)
            except IndexError:
                continue
            else:
                found_newlines += 1
        self.delete(self.pos, pos)

    def __str__(self):
        """
        Return the entire file as a string.

        .. warning:: The returned string may be too large to fit in RAM and
        cause a MemoryError.
        """
        return "".join(str(segment) for segment in self.segments)
