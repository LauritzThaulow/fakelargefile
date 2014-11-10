'''
Created on Nov 10, 2014

@author: lauritz
'''


from mock import Mock
from fakelargefile.segmenttail import OverlapSearcher


def test_index_iter_stop():
    os = OverlapSearcher("asdf")
    segment = Mock()
    segment.start = 11
    try:
        os.index_iter(segment, stop=10).next()
    except ValueError:
        assert True
    else:
        assert False
