'''
Created on Oct 25, 2014

@author: lauritz
'''


SI_PREFIX_DICT = {
    "k": 1024,
    "M": 1024**2,
    "G": 1024**3,
    "T": 1024**4}


class FakeLargeFile(object):
    def __init__(self, size, background=None):
        if isinstance(size, basestring):
            value, si_prefix = float(size[:-1]), size[-1:]
            self.size = int(SI_PREFIX_DICT[si_prefix] * value)
        else:
            self.size = size
        
        self.background = background
        self.pos = 0
        self.changes = []

    def insert(self, pos, text):
        self.changes.append(("I", pos, text))

    def delete(self, pos, byte_count):
        self.changes.append(("D", pos, byte_count))

    def change(self, pos, text):
        self.changes.append(("C", pos, text))

    def curr_pos(self, pos, change_index=0):
        for change_type, cpos, data in self.changes[change_index]:
            if cpos > pos:
                continue
            if change_type == "I":
                pos += len(data)
            elif change_type == "D":
                pos -= data
        return pos

    def reverse_pos_range(self, start, stop):
        old_intervals = [(start, stop)]
        for change_type, cpos, data in reversed(self.changes):
            cpos_stop = cpos + len(data)
            new_intervals = []
            for start, stop in old_intervals:
                if cpos > stop:
                    new_intervals.append((start, stop))
                    continue

    def read(self, byte_count):
        start = self.pos % len(self.background)
