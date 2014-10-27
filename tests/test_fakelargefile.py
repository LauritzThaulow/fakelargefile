'''
Created on Oct 25, 2014

@author: lauritz
'''


from fakelargefile import FakeLargeFile, NotFoundError
import pkg_resources


DEFAULT_BG = pkg_resources.resource_stream(
    "fakelargefile", "GPLv3.txt").read()


def test_next_occurence():
    flf = FakeLargeFile(27, "abcd\nefgh\n")
    assert flf.next_occurence("\n") == 4
    assert flf.next_occurence("\n", start=5) == 9
    assert flf.next_occurence("\n", start=10) == 14
    try:
        flf.next_occurence("\n", start=15, stop=19, after=True)
    except NotFoundError:
        assert True
    else:
        assert False
    assert flf.next_occurence("\n", start=15, stop=20) == 19
    assert flf.next_occurence("\n", start=15, stop=20, after=True) == 20
    assert flf.next_occurence("\n", start=20, after=True) == 25
    try:
        flf.next_occurence("\n", start=25)
    except NotFoundError:
        assert True
    else:
        assert False
    assert flf.pos == 0


def test_readline():
    flf = FakeLargeFile("1k", "a\nb\nc\n")
    assert flf.readline() == "a\n"
    assert flf.readline() == "b\n"
    assert flf.readline() == "c\n"
    assert flf.readline() == "a\n"
