'''
Created on Oct 25, 2014

@author: lauritz
'''


from fakelargefile import FakeLargeFile, RepeatingSegment

BG = """\
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

                            Preamble

  The GNU General Public License is a free, copyleft license for
software and other kinds of works.

  The licenses for most software and other practical works are designed
to take away your freedom to share and change the works.  By contrast,
the GNU General Public License is intended to guarantee your freedom to
share and change all versions of a program--to make sure it remains free
software for all its users.  We, the Free Software Foundation, use the
GNU General Public License for most of our software; it applies also to
any other work released this way by its authors.  You can apply it to
your programs, too.

"""


import logging


log = logging.getLogger(__name__)


def test_usage():
    flf = FakeLargeFile([RepeatingSegment.example(start=0, size="10G")])
    assert flf.readline().strip() == "GNU GENERAL PUBLIC LICENSE"
    deleted = flf.deleteline(count=2)
    assert flf.read(10).strip() == "Copyright"
    assert flf.readline() == (
        " (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>\n")
    flf.insert_literal(deleted)
    flf.seek(len(BG) * 10)
    assert flf.readline().strip() == "GNU GENERAL PUBLIC LICENSE"
    assert flf.readline().strip() == "Version 3, 29 June 2007"
    flf.seek(0, 2)
    fasit_end_pos = 10 * 1024 * 1024 * 1024
    assert flf.tell() == fasit_end_pos
    flf.seek(-10, 1)
    BG_pos = (fasit_end_pos - 10) % len(BG)
    fasit = (BG + BG)[BG_pos:BG_pos + 10]
    assert flf.read(10) == fasit
    flf.seek(len(BG))
    flf.delete(len(BG))
    assert flf.readline().strip() == "GNU GENERAL PUBLIC LICENSE"
