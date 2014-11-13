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

    This class defines the interface for a segment by specifying the name
    and signatures of some methods that each subclass must implement, and
    by implementing some other methods directly. It also sets the attributes
    common to all segment types. Those attributes are:

    - ``self.start``: the index of the first byte of this segment
    - ``self.stop``: the index of the first byte just past this segment
    - ``self.size``: the size of this segment, ``self.stop - self.start``

    These are the abstract methods that each subclass need to implement:

    - ``__str__`` (with memory limit)
    - ``substring`` (with memory limit)
    - ``index``
    - ``copy``
    - ``subsegment``
    - ``example`` (classmethod)

    The below methods are implemented directly in this class. Many of them
    call and depend on the abstract methods above for their functionality.

    - ``__repr__`` (gives ``repr(segment)`` a nice value)
    - ``__len__`` (makes ``len(segment) == segment.size``)
    - ``cut``
    - ``cut_at``
    - ``intersects``

    To build your own segment type, simply inherit from this class and
    override the abstract methods.

    .. warning::

       Segment types are meant to be immutable. Since we're all consenting
       adults here, the attributes of segment types are not protected from
       modification, beyond being hidden behind a read-only property. This
       is meant as a hint: you're not supposed to modify them because then
       Bad Things may happen.

    """

    __metaclass__ = ABCMeta

    repr_sample_max_length = 32

    def __init__(self, start, stop):
        """
        Initialize attributes common to all segment types.

        :param start: The start position of this segment, either as an int
            or as a string like "14.4k". See
            :py:func:`fakelargefile.tools.parse_unit` for acceptable syntax
            for the string.
        :type start: int or str

        :param stop: The position of the first byte beyond this segment,
            either as an int or as a string like "28.8k".
        :type start: int or str

        """
        self._start = parse_unit(start)
        self._stop = parse_unit(stop)
        self._size = self._stop - self._start
        if self._size == 0:
            raise ValueError("A segment must have a non-zero size")

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
        Return the size of this segment in bytes.
        """
        return self._size

    def intersects(self, start, stop):
        """
        Return True if the (start, stop) interval intersects this segment.

        Returns True even if the (start, stop) interval is of length 0, as
        long as it is properly *inside* this segment.

        Returns False if the start-stop interval is merely adjacent to this
        segment.
        """
        if self.start < stop < self.stop:
            return True
        elif self.start < start < self.stop:
            return True
        elif start < self.start < self.stop < stop:
            return True
        else:
            return False

    def cut(self, start, stop):
        """
        Return the parts left after removing part between start and stop.

        Cuts from and including start to and not including stop.

        The (start, stop) interval has to intersect this segment, or a
        ValueError is raised. However, either or both of start and stop
        may be beyond the boundaries of this segment.
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
        # TODO: index? position? consistency!
        if not (self.start <= index <= self.stop):
            raise ValueError(
                "The given index must be between {} and {}, got {}".format(
                    self.start, self.stop, index))
        return self.subsegment(None, index), self.subsegment(index, None)

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
        :return: A segment containing the same string as the given segment,
            or None if start == stop.

        """
        # TODO: automate param description and Slice creation for methods
        # accepting a slice.
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

    def __len__(self):
        """
        The lenght of the segment in bytes.
        """
        return self._size

    def __repr__(self):
        """
        A nice string representation of this segment.
        """
        # Do a string slice of substring in case of "\x00" bytes, which take
        # up 4 characters for every byte.
        sample_size = self.repr_sample_max_length
        sample_end_pos = min(self._stop, self._start + sample_size)
        str_sample = repr(
            self.substring(self._start, sample_end_pos)).strip("'")
        if sample_size < len(str_sample) or len(str_sample) < self._size:
            str_sample = "'{}'...".format(str_sample[:sample_size])
        else:
            str_sample = "'{}'".format(str_sample)
        return "{}(start={}, stop={}, str={})".format(
            type(self).__name__, self.start, self.stop, str_sample)
