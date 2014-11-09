'''
A file that's large on the inside but small on the outside.
'''


from __future__ import absolute_import, division

from fakelargefile.errors import NoContainingSegment
from fakelargefile.segment.chain import SegmentChain
from fakelargefile.segment.literal import LiteralSegment
from fakelargefile.segment.repeating import RepeatingSegment


class FakeLargeFile(SegmentChain):
    """
    A FakeLargeFile can mimic a very very large file.

    It does so by keeping track of segments of bytes. Each segment may be
    arbitrary large and contain explicit, procedurally generated or repeating
    content.

    The segments of a FakeLargeFile are always contiguous from the first
    to the last, and the first one always starts at 0.

    Here's a table of the computational complexity of various FakeLargeFile
    operations. Sibling methods like read() and readline() have the same
    complexity. N is the *count* of segments after the start of an insert or
    delete, B is the number of bytes an operation works on, M is the total
    number of segments.

    Method      Big O
    ======      ======
    seek()      O(1)
    tell()      O(1)
    read()      O(B)
    append()    O(1)
    insert()    O(N)
    delete()    O(N)
    write()     O(B)

    This means that FakeLargeFile is capable of feats that are very hard to
    do with normal files:

    - quickly rearranging, moving, inserting and deleting arbitrarily large
      segments of data

    - creating files whose non-null content is much larger than the
      available storage space

    """
    def __init__(self, segments=None):
        super(FakeLargeFile, self).__init__(segments, "\x00")
        self.pos = 0
        self.softspace = 0

    def readline(self, size=None):
        """
        Read up to and including the next newline character, and return it.

        :param int size: Maximum number of bytes to read. If set to None,
            which is the default, there is no limit.
        :returns: A string `s`, possibly including a newline, such that
            `len(s) >= size` when size is given.

        """
        line = []
        start_pos = self.pos
        for seg in self.segment_iter(self.pos):
            while True:
                line.append(seg.readline(self.pos))
                self.pos += len(line[-1])
                if size is not None and self.pos - start_pos >= size:
                    self.pos -= (self.pos - start_pos) - size
                    return "".join(line)[:size]
                if "\n" in line[-1]:
                    return "".join(line)
                else:
                    break
        return "".join(line)

    def deleteline(self, count=1):
        """
        Delete n lines starting from the current position.
        """
        found_newlines = 0
        pos = self.pos
        for pos in self.finditer("\n", self.pos, end_pos=True):
            found_newlines += 1
            if found_newlines == count:
                break
        deleted = self[self.pos:pos]
        self.delete(self.pos, pos)
        return deleted

    def seek(self, offset, whence=0):
        """
        Seek to a certain position in the file

        Implements the python file object seek functionality.

        It does not specify what to do if whence is not 0, 1 or 2. This method
        will raise a ValueError in that case.
        """
        if whence == 0:
            self.pos = offset
        elif whence == 1:
            self.pos += offset
        elif whence == 2:
            self.pos = self.size + offset
        else:
            raise ValueError("Valid values for whence is 0, 1 or 2.")

    def tell(self):
        """
        Return the current position in the file

        Implements the python file object tell functionality.
        """
        return self.pos

    def read(self, size=None):
        """
        Read up to size bytes, starting from the current position

        :param int size: The number of bytes to read. If set to None, which
            is the default, read until the end of the file.

        """
        if size is None:
            ret = self[self.pos:]
            self.pos = self.size
        else:
            ret = self[self.pos:self.pos + size]
            self.pos = self.pos + len(ret)
        return ret

    def write(self, string):
        """
        Write the string to the file at the current position.

        Any existing bytes will be overwritten.
        """
        if self.pos >= self.size:
            self.insert_literal(self.pos, string)
        else:
            segment = LiteralSegment(self.pos, string)
            self.overwrite(segment)

    def flush(self):
        """
        Do nothing, since there is no cache.
        """
        pass

    def __iter__(self):
        """
        Return an iterator for this object.
        """
        return self

    def next(self):
        """
        Return the next line, if at EOF, raise StopIteration
        """
        line = self.readline()
        if line:
            return line
        else:
            raise StopIteration

    def truncate(self, size=None):
        """
        Make the file this large by adding null bytes or deleting the end

        If size is not given, use the current position.

        If size is given, the current position is unchanged after the
        operation, even if it is then past the end of the file.
        """
        if size is None:
            size = self.pos
        if size > self.size:
            self.append(RepeatingSegment(self.size, size - self.size, "\x00"))
        else:
            self.delete(size, self.size)

    def writelines(self, sequence):
        """
        Write the sequence of strings to the file

        Does not add newlines to each string in sequence.
        """
        lines = "".join(sequence)
        self.overwrite(LiteralSegment(self.pos, lines))
        self.pos += len(lines)
