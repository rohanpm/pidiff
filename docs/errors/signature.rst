Signature changes
=================

Various changes to the signature of a callable will produce errors.


Error codes
-----------

====   =========================
Code   Name
====   =========================
B300   removed-argument
B310   added-argument
B320   moved-argument
B330   unpositional-argument
B340   removed-var-args
B350   removed-var-keyword-args
B800   uncallable
N400   added-optional-argument
N440   added-var-args
N450   added-var-keyword-args
====   =========================


Examples
--------

    .. index:: B300, removed-argument

    B300 removed-argument
        ::

            -def fn(x, y, z)
            +def fn(x, y)

            # breaks: fn('x', 'y', 'z')

        An argument was removed, breaking any clients who were formerly
        providing the argument.

    .. index:: B310, added-argument

    B310 added-argument
        ::

            -def fn(x, y)
            +def fn(x, y, z)

            # breaks: fn('x', 'y')

        A mandatory argument was added, breaking all clients formerly using
        the function.

    .. index:: B320, moved-argument

    B320 moved-argument
        ::

            -def scramble_eggs(with_butter=False, with_milk=True)
            +def scramble_eggs(with_milk=True, with_butter=False)

            # breaks: scramble_eggs(True, False)

        The position of an argument was changed, breaking clients passing
        the relevant argument(s) positionally.  Although, depending on the
        argument types, the call may be able to succeed, it's likely the
        semantics of the call have changed in a backwards-incompatible manner.

    .. index:: B330, unpositional-argument

    B330 unpositional-argument
        ::

            -def scramble_eggs(with_butter=False)
            +def scramble_eggs(*eggs, with_butter=False)

            # breaks: scramble_eggs(True)

        An argument could previously be provided positionally, but can now only
        be passed as a keyword argument.

    .. index:: B340, removed-var-args

    B340 removed-var-args
        ::

            -def max(*values)
            +def max(a, b)

            # breaks: max(10, 3, 7)

        A function previously accepted an unlimited number of positional
        arguments, and no longer does. This breaks any clients formerly passing
        more arguments than accepted by the new version of the function.

    .. index:: B350, removed-var-keyword-args

    B350 removed-var-keyword-args
        ::

            -def scramble_eggs(**kwargs)
            +def scramble_eggs(with_butter=False, with_milk=False)

            # breaks: scramble_eggs(with_salt=True)

        A function previously accepted an unlimited number of keyword
        arguments, and no longer does. This breaks any clients formerly passing
        any keyword arguments other than those supported by the new version of
        the function.

    .. index:: B800, uncallable

    B800 uncallable
        ::

             class EggScrambler:
            -  def __call__(self): ...
            +  def scramble_eggs(self): ...
             scrambler = EggScrambler()

            # breaks: scrambler()

        An object changed from callable to non-callable. This breaks any clients
        formerly using the object as a callable.

    .. index:: N400, added-optional-argument

    N400 added-optional-argument
        ::

            -def scramble_eggs(with_butter=False)
            +def scramble_eggs(with_butter=False, with_milk=True)

            # compatible: scramble_eggs(True)
            # new call:   scramble_eggs(True, True)

        A named argument was added with a default value. Since a default is supplied,
        this is a backwards-compatible change.

    .. index:: N440, added-var-args

    N440 added-var-args
        ::

            -def max(a, b)
            +def max(a, b, *rest)

            # compatible: max(10, 3)
            # new call:   max(10, 3, 7)

        A function now accepts any number of positional arguments.

    .. index:: N450, added-var-keyword-args

    N450 added-var-keyword-args
        ::

            -def scramble_eggs(with_butter=True)
            +def scramble_eggs(with_butter=True, **kwargs)

            # compatible: scramble_eggs(True)
            # new call:   scramble_eggs(True, with_salt=True)

        A function now accepts any number of named arguments.

