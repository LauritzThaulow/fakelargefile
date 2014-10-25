'''
Created on Oct 25, 2014

@author: lauritz
'''


from __future__ import absolute_import, division

from fakelargefile.errors import NotFoundError
import pkg_resources


SI_PREFIX_DICT = {
    "k": 1024,
    "M": 1024 ** 2,
    "G": 1024 ** 3,
    "T": 1024 ** 4}


class FakeLargeFile(object):
    def __init__(self, size, background=None):
        if isinstance(size, basestring):
            value, si_prefix = float(size[:-1]), size[-1:]
            self.size = int(SI_PREFIX_DICT[si_prefix] * value)
        else:
            self.size = size
        if background is None:
            background = pkg_resources.resource_stream(
                "fakelargefile", "GPLv3.txt").read()
        self.background = background
        self.pos = 0

    def next_occurence(self, string, start=0, stop=None, after=False):
        if stop is None:
            stop = self.size
        wrap = len(self.background)
        if stop - start > wrap:
            stop = start + wrap
        wrapped_start = start % wrap
        wrapped_stop = wrapped_start + (stop - start)
        bg = self.background * 3
        try:
            endpos = bg.index(string, wrapped_start, wrapped_stop)
        except ValueError:
            raise NotFoundError()
        unwrapped_endpos = (start // wrap) * wrap + endpos
        if after:
            return unwrapped_endpos + 1
        else:
            return unwrapped_endpos

    def readline(self, size=None):
        if size is None:
            try:
                endpos = self.background.index("\n", self.pos)
            except IndexError:
                endpos = self.size
        else:
            endpos = self.background.index("\n", self.pos, self.pos + size)
        ret = self.background[self.pos:endpos]
        self.pos = endpos
        return ret
