'''
A segment is an interval of bytes of a FakeLargeFile.
'''


from fakelargefile.segment.abc import (
    AbstractSegment, register_segment, segment_types)
from fakelargefile.segment.homogenous import HomogenousSegment
from fakelargefile.segment.literal import LiteralSegment
from fakelargefile.segment.repeating import RepeatingSegment
