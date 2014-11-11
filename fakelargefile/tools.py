'''
Various tools and auxiliary objects that this package needs.
'''

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


class abstractclassmethod(classmethod):

    __isabstractmethod__ = True

    def __init__(self, callable_):
        callable_.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(callable_)


def register_machinery():
    """
    Return a tuple (decorator, decorated) with a decorator and a list.

    The items decorated with the decorator will be added to the list called
    decorated.
    """
    list_ = []

    def register(cls):
        list_.append(cls)
        return cls

    return register, list_


SI_PREFIX_DICT = {
    "k": 1024,
    "M": 1024 ** 2,
    "G": 1024 ** 3,
    "T": 1024 ** 4}


def parse_size(size):
    """
    Parse size strings like "10G" or "1.5k" into exact number of bytes.

    If size is an int, simply return it.
    """
    if isinstance(size, basestring):
        value, si_prefix = float(size[:-1]), size[-1:]
        return int(SI_PREFIX_DICT[si_prefix] * value)
    else:
        return size


class Slice(object):
    """
    Calculate interesting attributes using the given segment slice.
    """
    def __init__(self, segment, start, stop, clamp=True):
        """
        Initialize a Slice instance.

        :param start: The start index of the slice, relative to the start of
            the file.
        :type start: int or NoneType
        :param stop: The global stop index of the slice, relative to the start
            of the file.
        :type stop: int or NoneType
        :param bool clamp: If True, which is the default, bring out of bounds
            values for start and stop to the closest possible value inside
            the bounds. If False, a ValueError is raised for out of bounds
            indices.

        """
        self.segment = segment
        self.clamp = clamp
        self._parse(start, stop)

    def _parse(self, start, stop):
        """
        Do the actual parsing of the slice.
        """
        seg = self.segment
        if start is None:
            start = seg.start
        if stop is None:
            stop = seg.stop
        if not (seg.start <= start <= stop <= seg.stop):
            if self.clamp:
                if stop < start:
                    raise ValueError(
                        "The start pos must be before the stop pos.")
                start = max(seg.start, start)
                stop = min(seg.stop, stop)
            else:
                raise ValueError((
                    "Arguments start={} and stop={} do not fulfill these "
                    "constraint:\n {} == self.start <= start <= stop <= "
                    "self.stop == {}").format(
                        start, stop, seg.start, seg.stop))
        self.start = start
        self.stop = stop
        self.local_start = start - seg.start
        self.local_stop = stop - seg.start
        self.size = stop - start
        self.slice = slice(start, stop)
        self.local_slice = slice(self.local_start, self.local_stop)
