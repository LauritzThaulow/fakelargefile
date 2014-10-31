'''
The abstract base class for segment types
'''


from __future__ import division, absolute_import

from abc import ABCMeta, abstractmethod

from fakelargefile.tools import (
    abstractclassmethod, register_machinery, parse_size)


register_segment, segment_types = register_machinery()


class AbstractSegment(object):

    __metaclass__ = ABCMeta

    def __init__(self, start, size):
        self._start = start
        self._size = parse_size(size)

    @property
    def start(self):
        return self._start

    @property
    def size(self):
        return self._size

    @property
    def stop(self):
        """
        Return the positon of the byte after the last byte of this segment.
        """
        return self.start + self.size

    def parse_slice(self, start, stop, local=False):
        """
        Convert start and stop slice attributes to actual indices.

        :param int start: If None, set to self.start.
        :param int stop: If None, set to self.stop.
        :param bool local: If True, return as a slice relative to the start
            of the segment.

        A ValueError is raised if this condition does not hold::

            self.start <= start <= stop <= self.stop
        """
        if start is None:
            start = self.start
        if stop is None:
            stop = self.stop
        if not (self.start <= start <= stop <= self.stop):
            raise ValueError((
                "Arguments start={} and stop={} do not fulfill the "
                "constraint {} == self.start <= start <= stop <= self.stop "
                "== {}").format(start, stop, self.start, self.stop))
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
        return False

    def intersects_segment(self, other):
        """
        Convenience method for self.intersects(other.start, other.stop)
        """
        return self.intersects(other.start, other.stop)

    def affected_by(self, index):
        """
        Will insertion or deletion at index affect this segment?

        It is assumed that it's not a zero-length deletion we're talking
        about.

        Being affected by means that this segment will be split, sliced
        and/or moved.
        """
        if not isinstance(index, int):
            raise ValueError()
        return index < self.stop

    def affected_by_segment(self, segment):
        """
        Will inserting or deleting the given segment affect this segment?

        Being affected by means that this segment will be split, sliced
        and/or moved.
        """
        return self.affected_by(segment.start)

    def cut(self, start, stop):
        """
        Parts left after removing part between start and stop.

        Cuts from and including start to and not including stop.

        The start to stop interval has to intersect self, or a ValueError is
        raised.
        """
        if not self.intersects(start, stop):
            raise ValueError(
                "Cant cut from {} to {} on segment from {} to {}".format(
                    start, stop, self.start, self.stop))
        if start <= self.start < stop < self.stop:
            return [self[stop:]]
        elif self.start < start < self.stop <= stop:
            return [self[:start]]
        elif self.start < start <= stop < self.stop:
            return [self[:start], self[stop:]]
        else:
            raise ValueError(
                "Unforseen case: does {}->{} intersect {}->{}".format(
                    start, stop, self.start, self.stop))

    def cut_at(self, index):
        """
        Cut self in two at the given index.

        Syntactic sugar for self.cut(index, index)
        """
        return self.cut(index, index)

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

    def __getitem__(self, slice_):
        """
        Generic slicing implementation.

        Implements these cases:

        - slice from start to some point in the middle
        - slice from some point in the middle to the end

        Any unsupported case will raise an IndexError.
        """
        if slice_.start is None and self.start < slice_.stop <= self.stop:
            return self.slice_from_start_to(slice_.stop)
        elif self.start <= slice_.start < self.stop and slice_.stop is None:
            return self.slice_to_stop_from(slice_.start)
        else:
            raise IndexError((
                "Unsupported slice operation. "
                "Start: {}, stop: {}, slice: {!r}").format(
                    self.start, self.stop, slice_))

    @abstractmethod
    def slice_from_start_to(self, stop):
        """
        Return the slice from the start of this segment to stop.
        """
        raise NotImplementedError()

    @abstractmethod
    def slice_to_stop_from(self, start):
        """
        Return the slice from start to the end of this segment.

        The start point of the returned segment should be such that::

            segment.slice_to_stop_from(x).start == segment.start + x
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
