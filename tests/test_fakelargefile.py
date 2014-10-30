'''
Created on Oct 25, 2014

@author: lauritz
'''


from mock import Mock
from fakelargefile import FakeLargeFile, LiteralSegment


def test___init__():
    segs = []
    for i in range(3):
        seg = Mock()
        seg.start = i + 5
        segs.append(seg)
    flf = FakeLargeFile(segs)
    assert flf.segments == segs
    assert flf.segment_start == list(range(5, 8))
    assert flf.pos == 0
    flf = FakeLargeFile()
    assert flf.segments == flf.segment_start == []


def test_first_affected_by():
    segs = [
        LiteralSegment(0, "Message "),
        LiteralSegment(8, "for "),
        LiteralSegment(12, "you "),
        LiteralSegment(16, "Sir!"),
        ]
    flf = FakeLargeFile(segs)
    assert flf.first_affected_by(LiteralSegment(8, "asdf")) == 1
    assert flf.first_affected_by(LiteralSegment(11, "asdf")) == 1
    assert flf.first_affected_by(LiteralSegment(12, "asdf")) == 2


def test_insert():
    flf = FakeLargeFile()
    flf.insert(LiteralSegment(start=0, text="a\nb"))
    flf.append(LiteralSegment(start=3, text="\nc\n"))
    assert flf.readline() == "a\n"
    assert flf.readline() == "b\n"
    assert flf.readline() == "c\n"
    flf.pos = 0
    flf.insert(LiteralSegment(start=1, text="iaiai, caramba!"))
    assert flf.readline() == "aiaiai, caramba!\n"
    assert flf.readline() == "b\n"
    assert flf.readline() == "c\n"
