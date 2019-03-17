Removed, Added Objects
======================

Errors are produced when all kinds of objects - classes, functions, methods
and other - are removed from or added to public API.

The ``removed-object``, ``added-object`` errors are a generic catch-all
for all kinds of objects. Where possible, an error is produced with a
more specific type.


Error codes
-----------

.. index:: B100, removed-object, B120, removed-function,
           B130, removed-method, B140, removed-class,
           N200, added-object, N220, added-function,
           N230, added-method, N240, added-class


====   ===================
Code   Name
====   ===================
B100   removed-object
B120   removed-function
B130   removed-method
B140   removed-class
N200   added-object
N220   added-function
N230   added-method
N240   added-class
====   ===================


Example
-------

Initial version of code:

.. code-block:: python

    # In cafe/__init__.py
    class CoffeeMachine:
        def make_cappucino(self, size):
            ...

        def make_latte(self, size):
            ...

        def make_black_tea(self, size):
            ...

Updated version:

.. code-block:: python

    # Now there's a default size
    DEFAULT_SIZE = 'large'

    class CoffeeMachine:
        def make_cappucino(self, size):
            ...

        def make_latte(self, size):
            ...

        # coffee machines don't make tea...
        #def make_black_tea(self, size):


This change will produce errors such as:

::

    cafe/__init__.py:0: N200 object added: DEFAULT_SIZE
    cafe/__init__.py:3: B120 function removed: make_black_tea
