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
    abstractclassmethod, register_machinery, parse_unit, Slice)


register_segment, segment_types = register_machinery()


class AbstractSegment(object):
    """
    Abstract Base Class for all segment types.

    Segment types are immutable by convention and usage. It *is* possible
    to change the attributes of a segment, but please don't.

    To build your own segment type, simply inherit from this class and
    override the abstract methods.
    """

    __metaclass__ = ABCMeta

    def __init__(self, start, stop):
        """
        Initialize attributes common to all segment types.

        This method permanently sets the values for the start, stop and size
        read-only properties.
        """
        self._start = parse_unit(start)
        self._stop = parse_unit(stop)
        self._size = self._stop - self._start

    @property
    def start(self):
        """
        Return the positon of the first byte of this segment.
        """
        return self._start

    @property
    def stop(self):
        """
        Return the positon of the byte after the last byte of this segment.
        """
        return self._stop

    @property
    def size(self):
        """
        Return the size of this segmflfent in bytes.
        """
        return self._size

    def intersects(self, start, stop):
        """
        Is part of the start-stop interval inside this segment?

        Returns True even if the start-stop interval is of length 0, as long
        as it is *inside* this segment.

        Returns False if the start-stop interval is merely adjacent to this
        segment.
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
        sl = Slice(start, stop, self.start, self.stop)
        result = []
        if self.start < sl.start:
            result.append(self.subsegment(self.start, sl.start))
        if sl.stop < self.stop:
            result.append(self.subsegment(sl.stop, self.stop))
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
        return self.subsegment(None, index), self.subsegment(index, None)

    def readline(self, pos):
        """
        Return the line starting at pos and ending after the next newline.

        The final line of the segment may not end in a newline.
        """
        # TODO: remove
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
        return self._size

    def __repr__(self):
        """
        A nice string representation of this segment.
        """
        return "{}(start={}, stop={})".format(
            type(self).__name__, self.start, self.stop)

    @abstractmethod
    def subsegment(self, start, stop):
        """
        Return a segment with the same data as this segment in the interval.

        .. note::

           This is an abstract method, to be implemented separately in each
           subclass.

        :param start: The start position of the returned segment. Use
            self.start if None. If less than self.start, use self.start.
        :type start: int or NoneType
        :param stop: The stop position of the returned segment. Use self.stop
            if None. If greater than self.stop, use self.stop.
        :type stop: int or NoneType
        :return: A segment containing the same string as the given segment.

        """
        raise NotImplementedError()

    @abstractclassmethod
    def example(cls, start, stop):  # @NoSelf
        """
        Return an example segment of this class with the given start and stop.

        .. note::

           This is an abstract method, to be implemented separately in each
           subclass.

        :param start: The file position the segment should start at. May be
            specified as an int or as a human readable string like "3M" for
            3 * 1024 * 1024 bytes. See
            :py:func:`fakelargefile.tools.parse_unit` for accepted syntax.
        :type start: int or str
        :param stop: The stop position, parsed the same way as the start
            position.
        :type stop: int or str
        """
        raise NotImplementedError()

    @abstractmethod
    def copy(self, start=None):
        """
        Return a copy of this segment, possibly shifted to start elsewhere.

        .. note::

           This is an abstract method, to be implemented separately in each
           subclass.

        """
        raise NotImplementedError()

    @abstractmethod
    def index(self, string, start=None, stop=None, end_pos=False):
        """
        Return the index of the next occurence of string.

        .. note::

           This is an abstract method, to be implemented separately in each
           subclass.

        :param str string: The string to search for
        :param int start: The index to start at, self.start by default. If
            less than self.start, use self.start.
        :param int stop: The index at which to stop searching, self.stop by
            default. If greater than self.stop, use self.stop.
        :param bool end_pos: Return the index after the end of the found
            string instead of the index of the beginning.

        If the string is not found, a ValueError will be raised.
        """
        raise NotImplementedError()

    @abstractmethod
    def substring(self, start, stop):
        """
        The substring from start to stop.

        .. note::

           This is an abstract method, to be implemented separately in each
           subclass. It should raise
           :py:class:`fakelargefile.errors.MemoryLimitError` if the resulting
           string will require memory beyond the set memory limit.

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

        .. note::

           This is an abstract method, to be implemented separately in each
           subclass. It should raise
           :py:class:`fakelargefile.errors.MemoryLimitError` if the resulting
           string will require memory beyond the set memory limit.

        """
        raise NotImplementedError()
