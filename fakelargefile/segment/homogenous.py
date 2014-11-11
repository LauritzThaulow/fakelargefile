'''
A segment which consists of only one repeated character
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


from fakelargefile.segment.abc import AbstractSegment, register_segment
from fakelargefile.tools import Slice


@register_segment
class HomogenousSegment(AbstractSegment):
    def __init__(self, start, size, char):
        super(HomogenousSegment, self).__init__(start, size)
        if not (isinstance(char, basestring) and len(char) == 1):
            raise ValueError(
                "Argument char must be a single byte, not {!r}.".format(char))
        self.char = char

    def subsegment(self, start, stop):
        sl = Slice(self, start, stop)
        return type(self)(sl.start, sl.size, self.char)

    @classmethod
    def example(cls, start, size):
        return cls(start=start, size=size, char="\x00")

    def copy(self, start=None):
        if start is None:
            start = self.start
        return type(self)(start, self.size, self.char)

    def index(self, string, start=None, stop=None, end_pos=False):
        # for there to be any match, string must be homogenous too
        if len(set(string)) > 1:
            raise ValueError()
        # and it must use the same character
        if string and string[0] != self.char:
            raise ValueError()
        sl = Slice(self, start, stop)
        if sl.size < len(string):
            raise ValueError()
        if end_pos:
            return sl.start + len(string)
        else:
            return sl.start

    def substring(self, start=None, stop=None):
        sl = Slice(self, start, stop, clamp=False)
        return self.char * sl.size

    def __str__(self):
        return self.char * self.size
