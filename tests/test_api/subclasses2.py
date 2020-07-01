class BaseClass:
    def fn(self, new_arg=None):
        pass

    def new_fn(self):
        pass

    @classmethod
    def new_classfn(cls):
        pass


class SubClassA(BaseClass):
    pass


class SubClassB(BaseClass):
    pass


__version__ = "1.0.1"
