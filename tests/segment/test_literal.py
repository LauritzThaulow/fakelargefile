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
    string = "abcdefghij"
    ls = LiteralSegment(start=17, string=string)
    assert ls.start == 17
    assert ls.string == str(ls) == string
    assert ls.size == 10
    try:
        ls.index("xyz")
    except ValueError:
        assert True
    else:
        assert False
