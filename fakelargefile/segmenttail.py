'''
A FIFO queue of segments whose capacity is determined by the combined lenghts
'''

from __future__ import absolute_import, division

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


from collections import deque


class OverlapSearcher(object):
    """
    Remember consecutive segments and search across their boundaries.
    """
    def __init__(self, string):
        """
        Initialize a OverlapSearcher instance.

        :param str string: The string to search for.

        """
        self.string = string
        self.overlap_size = len(string) - 1
        self.clear()

    def clear(self):
        """
        Clear all segment-related data.
        """
        self.segments = deque()
        self.length = 0

    def append(self, segment):
        """
        Add segment to one end and pop unneeded segments from the other end.
        """
        overlap_start = segment.stop - self.overlap_size
        if segment.start <= overlap_start:
            self.clear()
        else:
            overlap_start = segment.start
        # TODO: implement segment.subsegment?
        tail_tip = segment.right_part(overlap_start)
        self.segments.append(tail_tip)
        self.length += len(tail_tip)
        while self.length - len([0]) > self.overlap_size:
            self.length -= len(self.segments.popleft())

    def index_iter(self, next_segment):
        """
        Yield indices of all non-overlapping locations of search string.

        :param AbstractSegment next_segment: The segment which begins where
            the previously appended segment ends.

        This method combines the segments appended up to now with with
        a next_segment given in the arguments, and then yields the indices
        of all non-overlapping instances of the search string it finds in
        this combined string.

        This method is guaranteed to only return matches which cross the
        boundary between the previously appended segment and next_segment.
        """
        left_overlap = "".join(map(str, self.segments))[-self.overlap_size:]
        right_overlap = next_segment.substring(
            next_segment.start,
            min(next_segment.start + self.overlap_size, next_segment.stop))
        overlap_string = left_overlap + right_overlap
        overlap_pos = 0
        while True:
            try:
                overlap_pos = overlap_string.index(self.string, overlap_pos)
            except ValueError:
                break
            else:
                yield overlap_pos - len(left_overlap) + next_segment.start
                overlap_pos += len(self.string)
