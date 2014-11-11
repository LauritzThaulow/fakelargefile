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


from nose.tools import nottest

from fakelargefile.tools import Slice


@nottest
def int_test_Slice(clamp):
    sl = Slice(None, None, 7, 17)
    assert sl.start == 7
    assert sl.stop == 17
    assert sl.size == 10
    assert sl.local_start == 0
    assert sl.local_stop == 10
    assert sl.slice == slice(7, 17)
    assert sl.local_slice == slice(0, 10)
    sl = Slice(None, 15, 7, 17, clamp=clamp)
    assert sl.start == 7
    assert sl.stop == 15
    sl = Slice(10, None, 7, 17, clamp=clamp)
    assert sl.start == 10
    assert sl.stop == 17
    sl = Slice(11, 12, 7, 17, clamp=clamp)
    assert sl.start == 11
    assert sl.stop == 12
    sl = Slice(7, 17, 7, 17, clamp=clamp)
    assert sl.start == 7
    assert sl.stop == 17


def test_Slice_wo_clamp():
    int_test_Slice(False)


def test_Slice_w_clamp():
    int_test_Slice(True)


def test_Slice_clamp():
    sl = Slice(-1000, 1000, 7, 17)
    assert sl.start == 7
    assert sl.stop == 17
    for start, stop in ((6, 17), (7, 18), (15, 10)):
        try:
            Slice(start, stop, 7, 17, clamp=False)
        except ValueError:
            assert True
        else:
            assert False
