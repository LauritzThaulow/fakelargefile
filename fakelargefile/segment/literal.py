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
from fakelargefile.tools import parse_size


@register_segment
class LiteralSegment(AbstractSegment):
    def __init__(self, start, string):
        super(LiteralSegment, self).__init__(start, len(string))
        self.string = string

    def left_part(self, stop):
        return type(self)(self.start, self.string[:stop - self.start])

    def right_part(self, start):
        return type(self)(start, self.string[start - self.start:])

    @classmethod
    def example(cls, start, size):
        basis = pkg_resources.resource_stream(
            "fakelargefile", "GPLv3.txt").read()
        size = parse_size(size)
        basis = basis * (size // len(basis) + 1)
        return cls(start, basis[:size])

    def copy(self, start=None):
        if start is None:
            start = self.start
        return type(self)(start, self.string)

    def index(self, string, start=None, stop=None, end_pos=False):
        local_start, local_stop = self.parse_slice(start, stop, local=True)
        index = self.string.index(string, local_start, local_stop)
        if end_pos:
            index += len(string)
        return self.start + index

    def substring(self, start, stop):
        local_start, local_stop = self.parse_slice(start, stop, local=True)
        return self.string[local_start:local_stop]

    def __str__(self):
        return self.string
