'''
Created on Oct 25, 2014

@author: lauritz
'''


from fakelargefile import FakeLargeFile, LiteralSegment


def test_insert():
    flf = FakeLargeFile()
    flf.insert(LiteralSegment(start=0, text="a\nb"))
    flf.append(LiteralSegment(start=3, text="\nc\n"))
    assert flf.readline() == "a\n"
    assert flf.readline() == "b\n"
    assert flf.readline() == "c\n"
