class Outer1:
    def some_method(self):
        pass

    class Inner1:
        # a method was removed here
        def unchanged(self):
            pass

    Inner2 = Inner1


class Outer2:
    Inner = Outer1


class Outer3:
    class Inner:
        EvenMoreInner = Outer1.Inner1


Outer4 = Outer2
Outer5 = Outer3
Outer6 = Outer2
Outer7 = Outer3
