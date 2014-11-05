'''
A segment which consists of only one repeated character
'''


from fakelargefile.segment.abc import AbstractSegment, register_segment


@register_segment
class HomogenousSegment(AbstractSegment):
    def __init__(self, start, size, char):
        super(HomogenousSegment, self).__init__(start, size)
        if not (isinstance(char, basestring) and len(char) == 1):
            raise ValueError(
                "Argument char must be a single byte, not {!r}.".format(char))
        self.char = char

    def left_part(self, stop):
        return type(self)(self.start, stop - self.start, self.char)

    def right_part(self, start):
        return type(self)(start, self.stop - start, self.char)

    @classmethod
    def example(cls, start, size):
        return cls(start=start, size=size, char="\x00")

    def copy(self, start=None):
        if start is None:
            start = self.start
        return type(self)(start, self.size, self.char)

    def index(self, string, start=None, stop=None, end_pos=False):
        if len(set(string)) > 1:
            raise ValueError()
        if string and string[0] != self.char:
            raise ValueError()
        start, stop = self.parse_slice(start, stop)
        if stop - start < len(string):
            raise ValueError()
        if end_pos:
            return start + len(string)
        else:
            return start

    def substring(self, start=None, stop=None):
        start, stop = self.parse_slice(start, stop)
        return self.char * (stop - start)

    def __str__(self):
        return self.char * self.size
