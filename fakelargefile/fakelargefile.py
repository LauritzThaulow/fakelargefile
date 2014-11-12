'''
A file that's large on the inside but small on the outside.
'''

from __future__ import absolute_import, division

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

from fakelargefile.config import get_memory_limit
from fakelargefile.errors import MemoryLimitError
from fakelargefile.segmentchain import SegmentChain
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

    Here's a table to give you an informal impression of the computational
    complexity of various FakeLargeFile operations. The coefficients of the
    terms are unspecified. Sibling methods like read(), readline() and
    readlines() have the same complexity.

    - N is the *count* of segments following the start of an insert or delete
    - B is the number of bytes an operation works on
    - S is the number of segments an operation works on or covers
    - M is the total number of segments.

    ==========  ===================
    Method      Complexity
    ==========  ===================
    seek()      O(1)
    tell()      O(1)
    read()      O(log(M) + B)
    append()    O(1)
    insert()    O(log(M) + N)
    delete()    O(log(M) + (N - S))
    write()     O(log(M) + S + 1)
    truncate()  O(log(M) + 1)
    ==========  ===================

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
        current_length = 0
        for seg in self.segment_iter(self.pos):
            while True:
                line.append(seg.readline(self.pos))
                self.pos += len(line[-1])
                current_length = self.pos - start_pos
                if 2 * current_length > get_memory_limit():
                    raise MemoryLimitError((
                        "Readline would result in memory consumption larger "
                        "than the current memory limit, which is {}").format(
                            get_memory_limit()))
                if size is not None and current_length >= size:
                    self.pos -= current_length - size
                    return "".join(line)[:size]
                if "\n" in line[-1]:
                    return "".join(line)
                else:
                    break
        return "".join(line)

    def readlines(self, sizehint=None):
        """
        A list of all the lines left in the file

        :param int sizehint: If given, read to the next newline character
            after the self.pos + sizehint position.

        """
        if sizehint is None:
            sizehint = self.size - self.pos
        stop = self.pos + sizehint
        if stop - self.pos > get_memory_limit():
            raise MemoryLimitError((
                "Readlines would result in memory consumption larger "
                "than the current memory limit, which is {}").format(
                    get_memory_limit()))
        ret = []
        prev_pos = self.pos
        for pos in self.finditer("\n", self.pos, end_pos=True):
            ret.append(self[prev_pos:pos])
            if stop < pos:
                break
            prev_pos = pos
        return ret

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
        if self.size < size:
            self.append(RepeatingSegment(self.size, size, "\x00"))
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
