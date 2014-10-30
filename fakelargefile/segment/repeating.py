'''
A segment containing repeating text
'''


from fakelargefile.segment.abc import AbstractSegment, register_segment
import pkg_resources


@register_segment
class RepeatingSegment(AbstractSegment):
    def __init__(self, start, size, text):
        super(RepeatingSegment, self).__init__(start, size)
        self.text = text
        # For speedy wrapping operations
        self.text_thrice = text * 3

    def slice_from_start_to(self, stop):
        return type(self)(self.start, stop - self.start, self.text)

    def slice_to_stop_from(self, start):
        split_at = start - self.start
        text = self.text[split_at:] + self.text[:split_at]
        return type(self)(start, self.stop - start, text)

    @classmethod
    def example(cls, start, size):
        text = pkg_resources.resource_stream(
            "fakelargefile", "GPLv3.txt").read()
        return cls(start=start, size=size, text=text)

    def copy(self, start=None):
        if start is None:
            start = self.start
        return type(self)(start, self.size, self.text)

    def index(self, string, start=None, stop=None, end_pos=False):
        start, stop = self.parse_slice(start, stop, local=True)
        length = min(stop - start, self.size + len(string))
        in_text_start = start % self.size
        to_add = start - in_text_start
        assert to_add + in_text_start == start
        index = self.text_thrice.index(
            string, in_text_start, in_text_start + length)
        if end_pos:
            index += len(string)
        return self.start + to_add + index

    def substring(self, start, stop):
        start, stop = self.parse_slice(start, stop, local=True)
        length = stop - start
        rep_size = len(self.text)
        modulus_start = start % rep_size
        modulus_start_plus_size = modulus_start + length
        if length < 2 * rep_size:
            return self.text_thrice[modulus_start:modulus_start_plus_size]
        head = self.text[modulus_start:]
        tail = self.text[:stop % rep_size]
        size_multiple = length - len(head) - len(tail)
        assert size_multiple % rep_size == 0
        whole_lengths = size_multiple // rep_size
        return "".join([head, self.text * whole_lengths, tail])

    def __str__(self):
        return (self.text * (self.size // len(self.text) + 1))[:self.size]
