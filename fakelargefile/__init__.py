"""
A fake large file
"""


from __future__ import absolute_import

from fakelargefile.errors import NotFoundError
from fakelargefile.fakelargefile import FakeLargeFile, NoContainingSegment
from fakelargefile.segment import (
    LiteralSegment, RepeatingSegment, HomogenousSegment)
