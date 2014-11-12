'''
A segment which is a literal string

A FakeLargeFile composed entirely of LiteralSegments is not fake, but may
still be more useful than a plain old file.
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


import pkg_resources

from fakelargefile.segment.abc import AbstractSegment, register_segment
from fakelargefile.tools import parse_unit, Slice


@register_segment
class LiteralSegment(AbstractSegment):
    """
    A segment containing exactly a given string.
    """
    def __init__(self, start, string):
        """
        Initialize a LiteralSegment instance.

        :param int start: The start pos of the segment.
        :param str string: The string this segment should contain.

        """
        start = parse_unit(start)
        super(LiteralSegment, self).__init__(start, start + len(string))
        self.string = string

    def subsegment(self, start, stop):
        sl = Slice(start, stop, self.start, self.stop)
        return type(self)(sl.start, self.string[sl.local_slice])

    @classmethod
    def example(cls, start, stop):
        basis = pkg_resources.resource_stream(
            "fakelargefile", "GPLv3.txt").read()
        start = parse_unit(start)
        stop = parse_unit(stop)
        size = stop - start
        basis = basis * (size // len(basis) + 1)
        return cls(start, basis[:size])

    def copy(self, start=None):
        if start is None:
            start = self.start
        return type(self)(start, self.string)

    def index(self, string, start=None, stop=None, end_pos=False):
        sl = Slice(start, stop, self.start, self.stop)
        index = self.string.index(string, sl.local_start, sl.local_stop)
        if end_pos:
            index += len(string)
        return self.start + index

    def substring(self, start, stop):
        sl = Slice(start, stop, self.start, self.stop, clamp=False)
        return self.string[sl.local_slice]

    def __str__(self):
        return self.string
