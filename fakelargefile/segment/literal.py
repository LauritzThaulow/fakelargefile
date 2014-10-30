'''
A segment which is a literal string

A FakeLargeFile composed entirely of LiteralSegments is not fake, but may
still be more useful than a plain old file.
'''


import pkg_resources

from fakelargefile.segment.abc import AbstractSegment, register_segment
from fakelargefile.tools import parse_size


@register_segment
class LiteralSegment(AbstractSegment):
    def __init__(self, start, text):
        super(LiteralSegment, self).__init__(start, len(text))
        self.text = text

    def slice_from_start_to(self, stop):
        return type(self)(self.start, self.text[:stop - self.start])

    def slice_to_stop_from(self, start):
        return type(self)(start, self.text[start - self.start:])

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
        return type(self)(start, self.text)

    def index(self, string, start=None, stop=None, end_pos=False):
        local_start, local_stop = self.parse_slice(start, stop, local=True)
        index = self.text.index(string, local_start, local_stop)
        if end_pos:
            index += len(string)
        return self.start + index

    def substring(self, start, stop):
        local_start, local_stop = self.parse_slice(start, stop, local=True)
        return self.text[local_start:local_stop]

    def __str__(self):
        return self.text
