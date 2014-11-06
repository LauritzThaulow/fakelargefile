'''
Created on Oct 25, 2014

@author: lauritz
'''


from mock import Mock

from fakelargefile.errors import NoContainingSegment
from fakelargefile.segment.chain import SegmentChain
from fakelargefile.segment.literal import LiteralSegment

LS = LiteralSegment


def test___init__():
    segs = []
    for i in range(3):
        seg = Mock()
        seg.start = i * 3
        seg.stop = i * 3 + 3
        segs.append(seg)
    sc = SegmentChain(segs)
    assert sc.segments == segs
    assert sc.segment_start == [0, 3, 6]
    sc = SegmentChain()
    assert sc.segments == sc.segment_start == []


def test___init___fill_gaps():
    sc = SegmentChain([LS(1, "a"), LS(4, "a"), LS(10, "aa")])
    assert str(sc) == " a  a     aa"
    try:
        SegmentChain([LS(1, "a")], fill_gaps=False)
    except ValueError:
        assert True
    else:
        assert False
    sc = SegmentChain([LS(0, "a")], fill_gaps=False)
    try:
        sc.insert(LS(2, "a"))
    except ValueError:
        assert True
    else:
        assert False


def test_segment_containing():
    segs = [
        LS(0, "Message "),
        LS(8, "for "),
        LS(12, "you "),
        LS(16, "Sir!"),
        ]
    sc = SegmentChain(segs)
    assert sc.segment_containing(0) == 0
    assert sc.segment_containing(1) == 0
    assert sc.segment_containing(7) == 0
    assert sc.segment_containing(8) == 1
    assert sc.segment_containing(15) == 2
    assert sc.segment_containing(19) == 3
    try:
        sc.segment_containing(20)
    except NoContainingSegment:
        assert True
    else:
        assert False


def test_finditer():
    sc = SegmentChain()
    strings = [
        "This is one segment. ", "This is another. ", "This is the last one."]
    for string in strings:
        sc.append_literal(string)
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
    for idx in sc.finditer("is"):
        ret.append(idx)
    assert ret == fasit


def test_finditer_across_segments():
    sc = SegmentChain()
    string = "aafaffafffafffffafa"
    chunk = ""
    control = ""
    for char in string:
        if chunk == "" or char == chunk[-1]:
            chunk += char
        else:
            sc.append_literal(chunk)
            control += chunk
            chunk = char
    sc.append_literal(chunk)
    control += chunk
    assert control == string
    assert list(sc.finditer("afa")) == [1, 16]
    assert list(sc.finditer("fff")) == [7, 11]
    assert list(sc.finditer("ff")) == [4, 7, 11, 13]
    assert list(sc.finditer("f")) == [
        2, 4, 5, 7, 8, 9, 11, 12, 13, 14, 15, 17]
    assert list(sc.finditer("ffa", end_pos=True)) == [7, 11, 17]


def test_insert_and_append():
    sc = SegmentChain()
    sc.insert(LS(start=0, text="a\nb"))
    sc.append(LS(start=3, text="\nc\n"))
    assert str(sc) == "a\nb\nc\n"
    sc.insert(LS(start=1, text="iaiai, caramba!"))
    assert str(sc) == "aiaiai, caramba!\nb\nc\n"


def test_append_and___str__():
    sc = SegmentChain()
    sc.append(LS(0, "We've "))
    sc.append(LS(0, "got "))
    sc.append(LS(0, "sausage "))
    sc.append(LS(0, "and "))
    sc.append(LS(0, "bacon."))
    assert str(sc) == "We've got sausage and bacon."


def test_append_literal():
    test_text = """\
Liptauer?
No.
Lancashire?
No.
White Stilton?
No.
Danish Blue?
No.
"""
    lines = [x + "\n" for x in test_text.split("\n") if x]
    sc = SegmentChain()
    for line in lines:
        sc.append_literal(line)
    assert str(sc) == test_text


def test_delete():
    sc = SegmentChain()
    sc.append_literal("abcd")
    sc.append_literal(" hijk.")
    sc.delete(11, 16)
    sc.delete(8, 14)
    sc.delete(2, 4)
    assert str(sc) == "ab hij"


def test___getitem__():
    sc = SegmentChain()
    sc.append_literal("abc")
    sc.append_literal("defgh")
    sc.append_literal("ijklmn")
    assert sc[::-1] == "nmlkjihgfedcba"
    assert sc[3:1] == ""
    assert sc[1:3:-1] == ""
    assert sc[:] == "abcdefghijklmn"
    assert sc[::2] == "acegikm"
    assert sc[1::2] == "bdfhjln"


def test_insert_literal():
    sc = SegmentChain()
    sc.append_literal("I came here for a good argument.")
    sc.delete(17, 22)
    sc.insert_literal(17, "n")
    sc.delete(0, 1)
    sc.insert_literal(0, "No you didn't; no, you")
    assert str(sc) == "No you didn't; no, you came here for an argument."
