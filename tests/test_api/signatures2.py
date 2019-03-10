def mult(*args):
    # This change is broken because passing named x, y
    # would no longer work
    pass


def mult_safe1(x, y, *args):
    # This change is OK since x, y are still accepted
    pass


def mult_safe2(x, *args, **kwargs):
    # This change is also OK since y can still be accepted
    # whether it was given positionally or by keywords
    pass


def do_lots(data, someopt=True, newopt=None, otheropt=False, thisopt=None):
    # This change is broken since index of otheropt
    # and thisopt have changed
    pass
