def mult1(*args):
    # This change is major because passing named x, y
    # would no longer work
    pass


def mult2(x, **kwargs):
    # This change is major because passing positional y
    # would no longer work
    pass


def mult_minor1(x, y, *args):
    # This change is minor since x, y are still accepted
    pass


def mult_minor2(x, *args, **kwargs):
    # This change is also minor since y can still be accepted
    # whether it was given positionally or by keywords
    pass


def do_lots(data, otheropt=False, someopt=False, thisopt=None):
    # This change is major since index of otheropt
    # and someopt have changed
    pass


def do_lots_minor1(data, opt1=None, opt2=None):
    pass


def do_foo(x, y, z):
    pass


def mult_any(x, y, z, **kwargs):
    # Major break: *args was dropped
    pass


def do_anything(x, y, z, *args):
    # Major break: **kwargs was dropped
    pass
