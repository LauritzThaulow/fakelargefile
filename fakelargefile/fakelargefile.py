'''
Created on Oct 25, 2014

@author: lauritz
'''


from __future__ import absolute_import, division

from bisect import bisect_left
from itertools import islice


class NoneAffected(Exception):
    pass


class FakeLargeFile(object):
    def __init__(self, segments=None):
        if segments is None:
            segments = []
        self.segments = segments
        self.segment_start = [seg.start for seg in segments]
        self.pos = 0

    def first_affected_by(self, segment):
        """
        Index of first element of self.segments affected by the given segment.

        If no segments are affected, raise NoneAffected
        """
        for index, seg in enumerate(self.segments):
            if seg.affected_by_segment(segment):
                return index
        raise NoneAffected

    def current_segment_index(self):
        """
        Return the index of the segment which contains self.pos.

        If self.pos is at the end of the last segment, return
        len(self.segments).
        """
        index = bisect_left(self.segment_start, self.pos)
        if index == 0:
            # Special case for when self.pos == 0.
            return 0
        else:
            return index - 1

    def current_segment_iter(self):
        """
        Return an iterator over self.segments starting from the current one.

        The current one is the one which contains or starts with self.pos.
        """
        return islice(self.segments, self.current_segment_index(), None)

    def insert(self, segment):
        """
        Insert the segment, shift following bytes to the right.
        """
        try:
            first_affected = self.first_affected_by(segment)
        except NoneAffected:
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

    def append(self, segment):
        """
        Insert a copy of segment which start where the last segment stops.
        """
        last_segment_stop = self.segments[-1].stop
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
