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


__all__ = ["parse_unit", "Slice"]


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


def parse_unit(unit):
    """
    Parse unit strings like "10G" or "1.5k" into exact number of bytes.

    If size is an int, simply return it.
    """
    if isinstance(unit, basestring):
        value, si_prefix = float(unit[:-1]), unit[-1:]
        return int(SI_PREFIX_DICT[si_prefix] * value)
    else:
        return unit


class Slice(object):
    """
    Calculate useful attributes about a slice.

    The slice may be specified explicitly or implicitly. Both the start and
    stop arguments may be None to indicate that they're the minimum or
    maximum value, respectively.

    The actual start and stop values are then calculated and stored in the
    instance attributes, along with some derived values:

    ===========    =====================
    Attribute      Description
    ===========    =====================
    start          The start position relative to the start of the file.
    stop           The stop position relative to the start of the file.
    local_start    The start position relative to the given minimum.
    local_stop     The stop position relative to the given minimum.
    size           The value of start - stop.
    slice          An instance of the built-in slice type, slice(start, stop).
    local_slice    Same as above, but using the local start and stop.
    minimum        The minimum given as an argument.
    maximum        The maximum given as an argument.
    ===========    =====================

    """
    def __init__(self, start, stop, minimum, maximum, clamp=True):
        """
        Initialize a Slice instance.

        :param start: The start index of the slice, relative to the start of
            the file.
        :type start: int or NoneType
        :param stop: The global stop index of the slice, relative to the start
            of the file.
        :type stop: int or NoneType
        :param int minimum: The minimum value for start and stop.
        :param int maximum: The maximum value for start and stop.
        :param bool clamp: If True, which is the default, bring out of bounds
            values for start and stop to the closest possible value inside
            the bounds. If False, a ValueError is raised for out of bounds
            indices.

        """
        self.minimum = minimum
        self.maximum = maximum
        self.clamp = clamp
        self._parse(start, stop)

    def _parse(self, start, stop):
        """
        Do the actual parsing of the slice.
        """
        if start is None:
            start = self.minimum
        if stop is None:
            stop = self.maximum
        if not (self.minimum <= start <= stop <= self.maximum):
            if self.clamp:
                if stop < start:
                    raise ValueError(
                        "The start pos must be before the stop pos.")
                start = max(self.minimum, start)
                stop = min(self.maximum, stop)
            else:
                raise ValueError((
                    "Arguments start={} and stop={} do not fulfill these "
                    "constraint:\n {} <= start <= stop <= {}").format(
                        start, stop, self.minimum, self.maximum))
        self.start = start
        self.stop = stop
        self.local_start = start - self.minimum
        self.local_stop = stop - self.minimum
        self.size = stop - start
        self.slice = slice(start, stop)
        self.local_slice = slice(self.local_start, self.local_stop)
