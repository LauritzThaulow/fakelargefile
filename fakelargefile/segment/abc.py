'''
The abstract base class for segment types
'''

from __future__ import division, absolute_import

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

from abc import ABCMeta, abstractmethod

from fakelargefile.tools import (
    abstractclassmethod, register_machinery, parse_size)


register_segment, segment_types = register_machinery()


class AbstractSegment(object):

    __metaclass__ = ABCMeta

    def __init__(self, start, size):
        self._start = start
        self._size = parse_size(size)
        self._stop = start + self._size

    @property
    def start(self):
        """
        Return the positon of the first byte of this segment.
        """
        return self._start

    @property
    def size(self):
        """
        Return the size of this segment in bytes.
        """
        return self._size

    @property
    def stop(self):
        """
        Return the positon of the byte after the last byte of this segment.
        """
        return self._stop

    def parse_slice(self, start, stop, local=False, clamp=False):
        """
        Convert start and stop slice attributes to actual indices.

        :param int start: If None, set to self.start.
        :param int stop: If None, set to self.stop.
        :param bool local: If True, return indices relative to the start
            of the segment, instead of the default which is relative to the
            start of the file.
        :param bool clamp: If False, which is the default, a ValueError is
            raised for out of bounds indices. If True, the closest valid
            value is returned.
        :returns: A 2-tuple (start, stop) of indices.

        """
        if start is None:
            start = self.start
        if stop is None:
            stop = self.stop
        if not (self.start <= start <= stop <= self.stop):
            if clamp:
                if stop < start:
                    raise ValueError(
                        "The start pos must be before the stop pos.")
                start = max(self.start, start)
                stop = min(self.stop, stop)
            else:
                raise ValueError((
                    "Arguments start={} and stop={} do not fulfill these "
                    "constraint:\n {} == self.start <= start <= stop <= "
                    "self.stop == {}").format(
                        start, stop, self.start, self.stop))
        if local:
            start -= self.start
            stop -= self.start
        return start, stop

    def intersects(self, start, stop):
        """
        Return True if some part of the interval start-stop is inside self.

        Returns True even if start-stop is of length 0, *if* it is inside
        self.

        Returns False if start-stop is merely adjacent.
        """
        if self.start < stop < self.stop:
            return True
        elif self.start < start < self.stop:
            return True
        elif start < self.start < self.stop < stop:
            return True
        return False

    def cut(self, start, stop):
        """
        Parts left after removing part between start and stop.

        Cuts from and including start to and not including stop.

        The start to stop interval has to intersect self, or a ValueError is
        raised, but either or both may be beyond the boundaries of the
        segment.
        """
        if not self.intersects(start, stop):
            raise ValueError(
                "Cant cut from {} to {} on segment from {} to {}".format(
                    start, stop, self.start, self.stop))
        start, stop = self.parse_slice(start, stop, clamp=True)
        result = []
        if self.start < start:
            result.append(self.left_part(start))
        if stop < self.stop:
            result.append(self.right_part(stop))
        return result

    def cut_at(self, index):
        """
        Cut self in two at the given index.

        :param int index: The index to cut at, such that
            `self.start <= index <= self.stop`. If this does not hold, a
            ValueError is raised.
        :returns: A tuple (first, last), where either may be None if the cut
            is at self.start or self.stop.
        """
        if not (self.start <= index <= self.stop):
            raise ValueError(
                "The given index must be between {} and {}, got {}".format(
                    self.start, self.stop, index))
        return self.left_part(index), self.right_part(index)

    def readline(self, pos):
        """
        Return the line starting at pos and ending after the next newline.

        The final line of the segment may not end in a newline.
        """
        try:
            stop_index = self.index("\n", pos, end_pos=True)
        except ValueError:
            return self.substring(pos, None)
        else:
            return self.substring(pos, stop_index)

    def readlines(self, pos):
        """
        Return a list of all the lines starting at pos until the segment ends.

        The final line of the segment may not end in a newline.
        """
        ret = []
        while True:
            line = self.readline(pos)
            pos += len(line)
            ret.append(line)
            if pos == self.stop:
                return ret

    def __len__(self):
        """
        The lenght of the segment in bytes.
        """
        return self.size

    def __repr__(self):
        """
        A nice string representation of this segment.
        """
        return "{}(start={}, stop={})".format(
            type(self).__name__, self.start, self.stop)

    @abstractmethod
    def left_part(self, stop):
        """
        Return the subsegment from self.start to stop.

        If stop is outside of this segment, the result is undefined.
        """
        raise NotImplementedError()

    @abstractmethod
    def right_part(self, start):
        """
        Return the subsegment from start to self.stop.

        The returned segment is not moved, i.e. it starts at `start`.

        If start is outside of this segment, the result is undefined.
        """
        raise NotImplementedError()

    @abstractclassmethod
    def example(cls, start, size):  # @NoSelf
        """
        Return an example segment of this class with the given size and start.
        """
        raise NotImplementedError()

    @abstractmethod
    def copy(self, start=None):
        """
        Return a copy of this segment, possibly shifted to start elsewhere.

        This should always be true, no matter the value of ``x``::

            str(self) == str(self.copy(start=x))

        """
        raise NotImplementedError()

    @abstractmethod
    def index(self, string, start=None, stop=None, end_pos=False):
        """
        Return the index of the next occurence of text.

        :param str string: The text to search for
        :param int start: The index to start at, self.start by default.
        :param int stop: The index at which to stop searching, self.stop by
            default.
        :param bool end_pos: Return the index after the end of the found
            string instead of the index of the beginning.

        If the string is not found, a ValueError will be raised.
        """
        raise NotImplementedError()

    @abstractmethod
    def substring(self, start, stop):
        """
        The substring from start to stop.

        Valid values for start and stop are such that::

            self.start <= start <= stop <= self.stop

        Start and stop may also each be None, in which case it is set to
        self.start and self.stop, respectively.
        """
        raise NotImplementedError()

    @abstractmethod
    def __str__(self):
        """
        Return the entire object as a string.

        .. warning: Actually builds a string representation of something that
           may be extremely large. Doesn't care at all about memory
           consumption. Should only be used when you know this is not a
           problem.
        """
        raise NotImplementedError()
