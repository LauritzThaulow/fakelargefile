"""
A fake large file
"""

from __future__ import absolute_import

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

from fakelargefile.errors import (
    NoContainingSegment, MemoryLimitError)
from fakelargefile.fakelargefile import FakeLargeFile
from fakelargefile.segment import (
    LiteralSegment, RepeatingSegment, HomogenousSegment)
from fakelargefile.config import get_memory_limit, set_memory_limit

__all__ = [
    "FakeLargeFile", "NoContainingSegment", "LiteralSegment",
    "RepeatingSegment", "HomogenousSegment"]
