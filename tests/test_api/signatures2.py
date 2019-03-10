def mult(*args):
    # This change is major because passing named x, y
    # would no longer work
    pass


def mult_minor1(x, y, *args):
    # This change is minor since x, y are still accepted
    pass


def mult_minor2(x, *args, **kwargs):
    # This change is also minor since y can still be accepted
    # whether it was given positionally or by keywords
    pass


def do_lots(data, someopt=True, newopt=None, otheropt=False, thisopt=None):
    # This change is broken since index of otheropt
    # and thisopt have changed
    pass
