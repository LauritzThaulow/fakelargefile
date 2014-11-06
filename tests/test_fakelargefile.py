'''
Created on Oct 25, 2014

@author: lauritz
'''


from fakelargefile import FakeLargeFile, LiteralSegment

LS = LiteralSegment


def test___init__():
    flf = FakeLargeFile()
    assert flf.pos == 0


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


def test_write():
    flf = FakeLargeFile()
    flf.append_literal("asdf asdf asdf")
    flf.append_literal("qwerty")
    flf.seek(2)
    flf.write(" ")
    flf.seek(4)
    flf.write("e")
    flf.seek(7)
    flf.write("ible as h")
    flf.seek(18)
    flf.write(" dreams.")
    assert str(flf) == "as feasible as her dreams."


def test_readline():
    lines = [str(x) * x + "\n" for x in range(10)]
    flf = FakeLargeFile()
    flf.append_literal("".join(lines) + "abc")
    for line in lines:
        assert flf.readline() == line
    assert flf.readline() == "abc"


def test_seek():
    flf = FakeLargeFile()
    flf.append_literal("One, two, five!")
    flf.seek(5)
    assert flf.read(3) == "two"
    flf.seek(-5, 2)
    assert flf.read(4) == "five"
    flf.seek(-4, 1)
    assert flf.read(4) == "five"
    try:
        flf.seek(0, 3)
    except ValueError:
        assert True
    else:
        assert False


def test_tell():
    flf = FakeLargeFile()
    flf.append_literal(
        "Make sure the prince doesn't leave this room "
        "until I come and get him.")
    assert flf.tell() == 0
    flf.seek(5)
    assert flf.tell() == 5
    flf.seek(1000)
    assert flf.tell() == 1000
