'''
A segment is an interval of bytes of a FakeLargeFile.
'''

COPYING = """\
    This file is part of FakeLargeFile.

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

from fakelargefile.segment.abc import (
    AbstractSegment, register_segment, segment_types)
from fakelargefile.segment.homogenous import HomogenousSegment
from fakelargefile.segment.literal import LiteralSegment
from fakelargefile.segment.repeating import RepeatingSegment
