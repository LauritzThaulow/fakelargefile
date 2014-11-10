'''
Functional tests for the FakeLargeFile package.
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


from fakelargefile import (
    FakeLargeFile, RepeatingSegment, LiteralSegment, MemoryLimitError)

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


import time
import logging
from contextlib import contextmanager


log = logging.getLogger(__name__)


def test_usage():
    flf = FakeLargeFile([RepeatingSegment(start=0, size="1G", string=BG)])
    assert flf.readline().strip() == "GNU GENERAL PUBLIC LICENSE"
    deleted = flf.deleteline(count=2)
    assert flf.read(10).strip() == "Copyright"
    assert flf.readline() == (
        " (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>\n")
    insert_at_pos = flf.tell()
    flf.insert_literal(insert_at_pos, deleted)
    assert insert_at_pos == flf.tell()
    flf.seek(len(BG) * 10)
    assert flf.readline().strip() == "GNU GENERAL PUBLIC LICENSE"
    assert flf.readline().strip() == "Version 3, 29 June 2007"
    flf.seek(0, 2)
    fasit_end_pos = 1 * 1024 * 1024 * 1024
    assert flf.tell() == fasit_end_pos
    flf.seek(-10, 1)
    BG_pos = (fasit_end_pos - 10) % len(BG)
    fasit = (BG + BG)[BG_pos:BG_pos + 10]
    assert flf.read(10) == fasit
    flf.seek(len(BG) * 100)
    assert flf.readline().strip() == "GNU GENERAL PUBLIC LICENSE"
    flf.seek(len(BG) * 100)
    pos = flf.tell()
    flf.delete(pos, pos + len(BG))
    assert flf.readline().strip() == "GNU GENERAL PUBLIC LICENSE"


def test_remaining_file_like_object_methods():
    flf = FakeLargeFile()
    pos = 1000000000
    flf.seek(pos)
    flf.write("hi\nhello\ngood day")
    flf.flush()
    flf.seek(pos)
    assert flf.readline() == "hi\n"
    assert flf.next() == "hello\n"
    assert flf.read(1) == "g"
    assert flf.readline(1) == "o"
    assert flf.read() == "od day"
    try:
        flf.next()
    except StopIteration:
        assert True
    else:
        assert False
    flf.seek(pos)
    flf.truncate(1001)
    assert flf.tell() == pos
    flf.seek(0, 2)
    assert flf.tell() == 1001
    flf.writelines(["a\n", "b", "c\n"])
    flf.seek(1001)
    assert list(flf) == ["a\n", "bc\n"]
    assert flf.softspace == 0
    flf.softspace = 1
    assert flf.softspace == 1


@contextmanager
def takes_less_than(seconds):
    t = time.time()
    try:
        yield
    finally:
        duration = time.time() - t
        if duration > seconds:
            assert False, (
                "Operation should take less than {:.2f}s, took {:.2f}s."
                ).format(seconds, duration)


@contextmanager
def raises_oom_error():
    try:
        yield
    except MemoryLimitError:
        pass
    else:
        assert False, "Operation should have raised MemoryLimitError"


def test_oom_protection():
    rep_seg = RepeatingSegment(0, "1G", (
        "time that you can work to make more money to buy you things "
        "you need to save "))
    flf = FakeLargeFile()
    flf.append(LiteralSegment(0, "Think of all the "))
    flf.append(rep_seg)
    flf.append(rep_seg)
    with takes_less_than(0.1):
        flf.delete(100, 1000000000)
    flf.append(rep_seg)
    with raises_oom_error():
        flf.delete_and_return(100, 1000000000)
    with raises_oom_error():
        flf[:]
    with raises_oom_error():
        str(flf)
    with raises_oom_error():
        flf.readline()
    flf.seek(0)
    with raises_oom_error():
        flf.read()
