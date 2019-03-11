import logging


do_this = 'oops not callable now'

def do_that(x, y, *rest, key1=None, key2=None, **kwargs):
    pass


class DoOther:
    def __init__(self, x, y):
        pass

    def __dir__(self):
        # see what happens if dir() returns something inaccessible
        return ['notexist-prop']


do_other_instance = DoOther(1, 2)


def mult(a, b):
    pass


__version__ = '1.0.0.dev0'
