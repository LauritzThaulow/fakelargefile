'''
A segment containing repeating string
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


import logging

from fakelargefile.segment.abc import AbstractSegment, register_segment
from fakelargefile.tools import Slice
import pkg_resources


log = logging.getLogger(__name__)


@register_segment
class RepeatingSegment(AbstractSegment):
    def __init__(self, start, size, string):
        if len(string) == 1:
            log.warning(
                "It's more efficient to use HomogenousSegment instead of "
                "RepeatingSegment when the string to repeat is only one "
                "byte.")
        super(RepeatingSegment, self).__init__(start, size)
        self.string = string
        # For speedy wrapping operations
        self.string_thrice = string * 3

    def subsegment(self, start, stop):
        # TODO: make init args start, stop instead of start, size
        sl = Slice(self, start, stop)
        start_at = sl.local_start % len(self.string)
        string = self.string[start_at:] + self.string[:start_at]
        new_string_length = min(sl.size, len(self.string))
        if new_string_length < len(self.string):
            return type(self)(sl.start, sl.size, string[:new_string_length])
        else:
            return type(self)(sl.start, sl.size, string[:new_string_length])

    @classmethod
    def example(cls, start, size):
        string = pkg_resources.resource_stream(
            "fakelargefile", "GPLv3.txt").read()
        return cls(start=start, size=size, string=string)

    def copy(self, start=None):
        if start is None:
            start = self.start
        return type(self)(start, self.size, self.string)

    def index(self, string, start=None, stop=None, end_pos=False):
        sl = Slice(self, start, stop)
        in_string_start = sl.local_start % len(self.string)
        to_add = sl.local_start - in_string_start
        assert to_add + in_string_start == sl.local_start
        length = min(sl.size, len(self.string) + len(string))
        index = self.string_thrice.index(
            string, in_string_start, in_string_start + length)
        if end_pos:
            index += len(string)
        return self.start + to_add + index

    def substring(self, start, stop):
        sl = Slice(self, start, stop, clamp=False)
        rep_size = len(self.string)
        modulus_start = sl.local_start % rep_size
        if sl.size < 2 * rep_size:
            return self.string_thrice[modulus_start:modulus_start + sl.size]
        head = self.string[modulus_start:]
        tail = self.string[:sl.local_stop % rep_size]
        size_multiple = sl.size - len(head) - len(tail)
        assert size_multiple % rep_size == 0
        whole_lengths = size_multiple // rep_size
        return "".join([head, self.string * whole_lengths, tail])

    def __str__(self):
        return (self.string * (self.size // len(self.string) + 1))[:self.size]
