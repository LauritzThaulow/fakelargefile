'''
A chain of segment instances.
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

from bisect import bisect
from itertools import islice

from fakelargefile.config import get_memory_limit
from fakelargefile.errors import NoContainingSegment, MemoryLimitError
from fakelargefile.segment import LiteralSegment, RepeatingSegment
from fakelargefile.segmenttail import OverlapSearcher


class SegmentChain(object):
    """
    A SegmentChain is a sequence of contiguous segments.

    The segments are always contiguous from the first to the last, and the
    first one always starts at 0.
    """
    def __init__(self, segments=None, fill_gaps="\x00"):
        """
        Initialize a SegmentChain.

        :param list segments: A list of instances implementing the Segment
            interface. They will be applied in order, the first ones possibly
            being partly or wholly overwritten by the following ones.
        :param str fill_gaps: If there are gaps between the segments, on init
            or by later insertion, fill them with RepeatingSegment instances
            using the given string. If the fill_gaps value evaluates to False,
            a ValueError will be raised instead if the segments are not
            contiguous.

        """
        if segments is None:
            segments = []
        self.size = 0
        self.fill_gaps = fill_gaps
        self.init_segments(segments)

    def update_size(self):
        """
        Set the size attribute to the position after the last segment
        """
        if self.segments:
            self.size = self.segments[-1].stop
        else:
            self.size = 0

    def fill_gap(self, start, stop):
        """
        Return a RepeatingSegment instance which fills the given gap.

        Uses the string self.fill_gaps as repeating pattern, except if it
        is a value which evaluates to False, in which case a ValueError will
        be raised instead.
        """
        if self.fill_gaps:
            return RepeatingSegment(start, stop - start, self.fill_gaps)
        else:
            raise ValueError("That segment is not contiguous with the rest.")

    def init_segments(self, segments):
        """
        Check the provided segments and append each to this FakeLargeFile.
        If the segments are not contiguous starting from 0, raise ValueError.
        """
        self.segments = []
        self.segment_start = []
        for seg in segments:
            self.overwrite(seg)

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

    def finditer(self, string, start=0, stop=None, end_pos=False):
        """
        Iterate over indices of occurences of string.

        :param str string: The string to search for.
        :param int start: Where to start searching. Default is 0.
        :param int stop: Where to stop searching. If not given or None,
            self.stop is used.
        :param bool end_pos: If False, which is the default, yield the
            indices of the start of the matches. If True, yield the indices
            of the first byte after each match.

        """
        pos = start
        if stop is None:
            stop = self.size
        overlap = OverlapSearcher(string)
        for seg in self.segment_iter(start):
            if stop <= seg.start:
                return
            # Yield indices that would not be found in any segment because
            # the search string is split across segments
            for index in overlap.index_iter(seg, stop, end_pos):
                yield index
            if pos != start:
                pos = overlap.pos
            while True:
                try:
                    pos = seg.index(string, pos, stop, end_pos=end_pos)
                except ValueError:
                    overlap.append(seg)
                    pos = seg.stop
                    break
                else:
                    yield pos
                    if not end_pos:
                        pos += len(string)

    def index(self, string, start=None, stop=None, end_pos=False):
        """
        Return index of the given string, raise ValueError if not found.

        :param str string: The string to find the next index of.
        :param int start: The positon at which to start searching, or None
            to start at the beginning.
        :param int stop: The positon at which to stop searching, or None to
            stop at the end.
        :param bool end_pos: If given, return the position following the end
            of the string, instead of the position of the start of the string.
        """
        for index in self.finditer(string, start, stop, end_pos):
            return index
        raise ValueError()

    def insert(self, segment):
        """
        Insert the segment, shift following bytes to the right.
        """
        try:
            first_affected = self.segment_containing(segment.start)
        except NoContainingSegment:
            to_append = []
            if self.size < segment.start:
                to_append.append(self.fill_gap(self.size, segment.start))
            to_append.append(segment)
            self.segments.extend(to_append)
            self.segment_start.extend([x.start for x in to_append])
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

    def insert_literal(self, start, string):
        """
        Convenience method for inserting a string at position ``start``
        """
        self.insert(LiteralSegment(start, string))

    def _delete(self, start, stop):
        """
        Internal partial delete method that does just the deleting.

        Internal because it breaks the "rule" of there never being any gaps
        between the segments. This rule breaking has to be temporary. It's up
        to the calling method to fix it, probably by filling the hole with
        something else.
        """
        try:
            first_affected = self.segment_containing(start)
        except NoContainingSegment:
            return len(self.segments), len(self.segments), [], []
        else:
            segment = self.segments[first_affected]
            if segment.start == start:
                before = []
            else:
                before = [segment.subsegment(None, start)]

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
                after = [segment.subsegment(stop, None)]

        return first_affected, last_affected + 1, before, after

    def delete(self, start, stop, return_deleted=False):
        """
        Delete from start to stop.

        :param int start: The position at which to start deleting
        :param int stop: The position after the last byte to delete
        :param bool return_deleted: If True, return what was deleted as a
            string.

        """
        if return_deleted:
            ret = self[start:stop]
        else:
            ret = None
        start_idx, stop_idx, before, after = self._delete(start, stop)
        replacement = before[:]
        if after:
            replacement.append(after[0].copy(start=start))
        for seg in self.segments[stop_idx:]:
            replacement.append(seg.copy(start=seg.start - (stop - start)))
        self.segments[start_idx:] = replacement
        self.segment_start[start_idx:] = [
            seg.start for seg in replacement]
        self.update_size()
        return ret

    def delete_to(
            self, start, string, count=1, end_pos=True,
            return_deleted=False):
        """
        Delete by search string.

        :param int start: The start point of the deletion and the start point
            of the search for string.
        :param str string: The string to search for. If no match is found,
            delete to the end of the file.
        :param int count: How many repeated searches to perform before
            returning.
        :param bool end_pos: If False, don't delete the last match. If True,
            which is the default, delete the last match too.
        :param bool return_deleted: If True, return the deleted segment parts
            as a string.
        :return: If return_deleted == True, return a list of strings if count
            > 1 or a single string if count == 1. If return_deleted == False,
            return None.

        """
        if count == 0:
            return
        ret = []
        delete_start = start
        pos_iter = self.finditer(string, start, end_pos=end_pos)
        for i, pos in enumerate(pos_iter, 1):
            if return_deleted:
                ret.append(self[delete_start:pos])
            if i == count:
                break
            delete_start = pos
        else:
            pos = self.size

        self.delete(start, pos)
        if return_deleted:
            if count == 1:
                return ret[0]
            else:
                return ret
        else:
            return None

    def deleteline(self, start, return_deleted=False):
        """
        Delete one line including newline starting from the given position.

        :param int start: Start deleting at this position.
        :param bool return_deleted: If True, return what was deleted as a
            string.

        """
        return self.delete_to(start, "\n", 1, True, return_deleted)

    def deletelines(self, start, count, return_deleted=False):
        """
        Delete the given number of lines starting from the given position.
        """
        return self.delete_to(start, "\n", count, True, return_deleted)

    def overwrite(self, segment, return_deleted=False):
        """
        Overwrite any existing data with the given segment.

        :param AbstractSegment segment: The segment to write.
        :param bool return_deleted: If True, return what was deleted as a
            string.

        """
        if return_deleted:
            ret = self[segment.start:segment.stop]
        else:
            ret = None
        if segment.start < self.size:
            start_idx, stop_idx, before, after = self._delete(
                segment.start, segment.stop)
            replacement = before + [segment] + after
            self.segments[start_idx:stop_idx] = replacement
            self.segment_start[start_idx:stop_idx] = [
                seg.start for seg in replacement]
            self.update_size()
        else:
            if self.size < segment.start:
                self.append(self.fill_gap(self.size, segment.start))
            self.append(segment)
        return ret

    def append(self, segment):
        """
        Insert a segment which start where the last segment stops.
        """
        if self.size == segment.start:
            self.segments.append(segment)
        else:
            self.segments.append(segment.copy(start=self.size))
        self.segment_start.append(self.size)
        self.update_size()

    def append_literal(self, string):
        """
        Append a LiteralSegment with the given string
        """
        self.segments.append(LiteralSegment(self.size, string))
        self.segment_start.append(self.size)
        self.update_size()

    def __str__(self):
        """
        Return the entire file as a string.

        .. warning:: The returned string may be too large to fit in RAM and
        cause a MemoryError.
        """
        return self[:]

    def __len__(self):
        """
        Return the length of this SegmentChain
        """
        return self.size

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
        # check if step moves in the wrong direction
        if (stop - start) * step < 0:
            return ""
        # make it so that start < stop. We'll reverse at the end.
        if step < 0:
            start, stop = stop + 1, start + 1
        # if the requested string is too large, protest!
        required_memory = 2 * (stop - start)
        memory_limit = get_memory_limit()
        if required_memory > memory_limit:
            raise MemoryLimitError((
                "Operation would require more more than {} bytes of ram, "
                "the current limit is {} bytes.").format(
                    required_memory, memory_limit))
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
