class OuterClass:
    class InnerClass:
        def __init__(self):
            self.x = "x"
            self.z = "z"

        @property
        def y(self):
            # note this one changed from attribute in __init__ to a @property
            return "y"

        def other_fn(self):
            pass

    InnerClass.set_from_outer = 123  # type: ignore

    def __init__(self):
        self.foo = "foo"
        self.bar = "bar"
        # note this one changed from @property to attribute assigned in __init__
        self.baz = "baz"
        self.quux = "quux"
        self._private_thing = 123
