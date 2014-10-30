'''
Created on Oct 25, 2014

@author: lauritz
'''


from mock import Mock
from fakelargefile import FakeLargeFile, LiteralSegment

LS = LiteralSegment


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
        LS(0, "Message "),
        LS(8, "for "),
        LS(12, "you "),
        LS(16, "Sir!"),
        ]
    flf = FakeLargeFile(segs)
    assert flf.first_affected_by(LS(8, "asdf")) == 1
    assert flf.first_affected_by(LS(11, "asdf")) == 1
    assert flf.first_affected_by(LS(12, "asdf")) == 2


def test_insert():
    flf = FakeLargeFile()
    flf.insert(LS(start=0, text="a\nb"))
    flf.append(LS(start=3, text="\nc\n"))
    assert flf.readline() == "a\n"
    assert flf.readline() == "b\n"
    assert flf.readline() == "c\n"
    flf.pos = 0
    flf.insert(LS(start=1, text="iaiai, caramba!"))
    assert flf.readline() == "aiaiai, caramba!\n"
    assert flf.readline() == "b\n"
    assert flf.readline() == "c\n"


def test_append_and___str__():
    flf = FakeLargeFile()
    flf.append(LS(0, "We've "))
    flf.append(LS(0, "got "))
    flf.append(LS(0, "sausage "))
    flf.append(LS(0, "and "))
    flf.append(LS(0, "bacon."))
    assert str(flf) == "We've got sausage and bacon."


def test_append_literal():
    flf = FakeLargeFile()
    flf.append_literal("""\
Liptauer?
No.
Lancashire?
No.
White Stilton?
No.
Danish Blue?
No.
""")
    assert flf.readline() == "Liptauer?\n"
    assert flf.deleteline(2) == "No.\nLancashire?\n"
    flf.readline()
    assert flf.deleteline(3) == "White Stilton?\nNo.\nDanish Blue?\n"
    assert str(flf) == """\
Liptauer?
No.
No.
"""