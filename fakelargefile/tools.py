'''
Various tools and auxiliary objects that this package needs.
'''


class abstractclassmethod(classmethod):

    __isabstractmethod__ = True

    def __init__(self, callable_):
        callable_.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(callable_)


def register_machinery():
    """
    Return a tuple (decorator, decorated) with a decorator and a list.

    The items decorated with the decorator will be added to the list called
    decorated.
    """
    list_ = []

    def register(cls):
        list_.append(cls)
        return cls

    return register, list_


SI_PREFIX_DICT = {
    "k": 1024,
    "M": 1024 ** 2,
    "G": 1024 ** 3,
    "T": 1024 ** 4}


def parse_size(size):
    """
    Parse size strings like "10G" or "1.5k" into exact number of bytes.

    If size is an int, simply return it.
    """
    if isinstance(size, basestring):
        value, si_prefix = float(size[:-1]), size[-1:]
        return int(SI_PREFIX_DICT[si_prefix] * value)
    else:
        return size
