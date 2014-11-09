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

from fakelargefile.segment import HomogenousSegment


log = logging.getLogger(__name__)


def test_HomogenousSegment():
    hs = HomogenousSegment(start=3, size=8, char="\x00")
    assert hs.start == 3
    assert hs.stop == 11
    assert hs.size == 8
    assert str(hs) == "\x00" * 8
    assert hs.index("\x00", 9, 11, end_pos=True) == 10
    assert hs.index("\x00" * 2, 9, 11, end_pos=True) == 11
    index_test_args = (
        ("ab", None, None), ("a", None, None), ("\x00", 9, 4),
        ("\x00" * 9, None, None))
    for tpl in index_test_args:
        try:
            hs.index(*tpl)
        except ValueError:
            assert True
        else:
            assert False
    try:
        HomogenousSegment(start=0, size=8, char="aa")
    except ValueError:
        assert True
    else:
        assert False
