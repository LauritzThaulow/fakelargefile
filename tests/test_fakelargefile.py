'''
Created on Oct 25, 2014

@author: lauritz
'''


from fakelargefile import FakeLargeFile


def test_init():
    flf = FakeLargeFile("1k")
    assert flf.size == 1024
    flf = FakeLargeFile("3.31254M")
    assert flf.size == int(1024 * 1024 * 3.31254)
    flf = FakeLargeFile("13G")
    assert flf.size == 13 * 1024 * 1024 * 1024
