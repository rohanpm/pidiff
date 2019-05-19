class OuterClass:
    class InnerClass:
        def __init__(self):
            self.x = 'x'
            if True:
                self.y = 'y'
            z = 'z'

            o = object()
            o.something = 'someval'

            # This can parse, though it's nonsense
            (2 + 2).result = 5

        @property
        def q(self):
            return 'q'

        def other_fn(self):
            # Not expected to be covered by the tool
            self.set_in_other_fn = None

    def __init__(self):
        self.foo = 'foo'
        self.bar = 'bar'

    @property
    def baz(self):
        return 'baz'
