'''
Tests for the fakelargefile.segment.homogenous submodule
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


import logging

from fakelargefile.segment import LiteralSegment


log = logging.getLogger(__name__)


def test_LiteralSegment():
    text = "abcdefghij"
    ls = LiteralSegment(start=17, text=text)
    assert ls.start == 17
    assert ls.text == str(ls) == text
    assert ls.size == 10
    try:
        ls.index("xyz")
    except ValueError:
        assert True
    else:
        assert False
    assert ls.readline(20) == "defghij"
    ls = LiteralSegment(start=4, text="as\ndf\ngh\n")
    lines = ls.readlines(5)
    log.debug(lines)
    assert lines == ["s\n", "df\n", "gh\n"]
