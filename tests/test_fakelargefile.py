'''
Created on Oct 25, 2014

@author: lauritz
'''


from mock import Mock
from fakelargefile import FakeLargeFile, LiteralSegment, NoContainingSegment

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


def test_segment_containing():
    segs = [
        LS(0, "Message "),
        LS(8, "for "),
        LS(12, "you "),
        LS(16, "Sir!"),
        ]
    flf = FakeLargeFile(segs)
    assert flf.segment_containing(0) == 0
    assert flf.segment_containing(1) == 0
    assert flf.segment_containing(7) == 0
    assert flf.segment_containing(8) == 1
    assert flf.segment_containing(15) == 2
    assert flf.segment_containing(19) == 3
    try:
        flf.segment_containing(20)
    except NoContainingSegment:
        assert True
    else:
        assert False


def test_finditer():
    flf = FakeLargeFile()
    strings = [
        "This is one segment. ", "This is another. ", "This is the last one."]
    for string in strings:
        flf.append_literal(string)
    concat = "".join(strings)
    fasit = []
    idx = 0
    while True:
        try:
            found_idx = concat.index("is", idx)
        except ValueError:
            break
        else:
            fasit.append(found_idx)
            idx = found_idx + 1
    ret = []
    for idx in flf.finditer("is"):
        ret.append(idx)
    assert ret == fasit


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
    deleted = flf.deleteline(2)
    assert deleted == "No.\nLancashire?\n"
    flf.readline()
    assert flf.deleteline(3) == "White Stilton?\nNo.\nDanish Blue?\n"
    assert str(flf) == """\
Liptauer?
No.
No.
"""


def test_delete():
    flf = FakeLargeFile()
    flf.append_literal("abcd")
    flf.append_literal(" hijk.")
    flf.delete(11, 16)
    flf.delete(8, 14)
    flf.delete(2, 4)
    assert str(flf) == "ab hij"


def test___getitem__():
    flf = FakeLargeFile()
    flf.append_literal("abc")
    flf.append_literal("defgh")
    flf.append_literal("ijklmn")
    print flf[::-1]
    assert flf[::-1] == "nmlkjihgfedcba"
    assert flf[3:1] == ""
    assert flf[1:3:-1] == ""
    assert flf[:] == "abcdefghijklmn"
    assert flf[::2] == "acegikm"
    assert flf[1::2] == "bdfhjln"


def test_read():
    flf = FakeLargeFile()
    flf.append_literal("a")
    flf.append_literal("bc")
    flf.append_literal("def")
    flf.append_literal("ghij")
    assert flf.read(1) == "a"
    assert flf.read(3) == "bcd"
    assert flf.read(5) == "efghi"
    assert flf.read(1) == "j"
    assert flf.read(1) == ""
    assert flf.read(1) == ""
