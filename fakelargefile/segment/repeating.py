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


from fakelargefile.segment.abc import AbstractSegment, register_segment
import pkg_resources


@register_segment
class RepeatingSegment(AbstractSegment):
    def __init__(self, start, size, string):
        super(RepeatingSegment, self).__init__(start, size)
        self.string = string
        # For speedy wrapping operations
        self.string_thrice = string * 3

    def left_part(self, stop):
        return type(self)(self.start, stop - self.start, self.string)

    def right_part(self, start):
        split_at = (start - self.start) % len(self.string)
        string = self.string[split_at:] + self.string[:split_at]
        return type(self)(start, self.stop - start, string)

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
        start, stop = self.parse_slice(start, stop, local=True, clamp=True)
        in_string_start = start % len(self.string)
        to_add = start - in_string_start
        assert to_add + in_string_start == start
        length = min(stop - start, len(self.string) + len(string))
        index = self.string_thrice.index(
            string, in_string_start, in_string_start + length)
        if end_pos:
            index += len(string)
        return self.start + to_add + index

    def substring(self, start, stop):
        start, stop = self.parse_slice(start, stop, local=True)
        length = stop - start
        rep_size = len(self.string)
        modulus_start = start % rep_size
        modulus_start_plus_size = modulus_start + length
        if length < 2 * rep_size:
            return self.string_thrice[modulus_start:modulus_start_plus_size]
        head = self.string[modulus_start:]
        tail = self.string[:stop % rep_size]
        size_multiple = length - len(head) - len(tail)
        assert size_multiple % rep_size == 0
        whole_lengths = size_multiple // rep_size
        return "".join([head, self.string * whole_lengths, tail])

    def __str__(self):
        return (self.string * (self.size // len(self.string) + 1))[:self.size]
