Removed, Added Modules
======================

Errors are produced when modules are added to or removed
from the namespace of a module within the public API.

The ``external-module`` errors are used when the added/removed
module is outside of the public API root.


Error codes
-----------

.. index:: B110, removed-module, B111, removed-external-module,
           N210, added-module, N211, added-external-module

====   ========================
Code   Name
====   ========================
B110   removed-module
B111   removed-external-module
N210   added-module
N211   added-external-module
====   ========================


Example: adding internal module
-------------------------------

Initial version of code:

.. code-block:: python

    # in kitchen/__init__.py
    def fry(eggs):
        return FryingPan().fry(eggs)

Updated version of code:

.. code-block:: python

    from kitchen.containers import cabinet

    def fry(eggs):
        return cabinet.find(FryingPan).fry(eggs)

As an (internal) module has been added to the namespace,
an error will be produced:

::

    kitchen/__init__.py:0: N210 module added: cabinet

This constitutes a minor API change since new code
could be written including ``from kitchen import cabinet``,
which would not work with the older version of the code.




Example: removing external module
---------------------------------

Initial version of code uses ``re`` module for regular expressions:

.. code-block:: python

    # in haystack/__init__.py
    import re

    class Haystack:
        def search(self, needle):
            return re.search(needle, self._content)

Updated version of code migrated to ``regex`` module:

.. code-block:: python

    import regex

    class Haystack:
        def search(self, needle):
            return regex.search(needle, self._content)

This change will produce an error for the major API change
of removing a formerly available module (as well as the
less severe change of adding a new module).  Since ``re``
lives outside of the ``haystack`` namespace, the module is
referred to as "external".

::

    haystack/__init__.py:0: B111 external module removed: re
    haystack/__init__.py:0: N211 external module added: regex


Discussion
----------

Adding a module is, of course, often expected when adding new functionality.
However, it can also happen accidentally as a result of changing
implementation.

The first example above shows how this can result in the same module
becoming available under multiple paths.  In that example, with the
new version of the code, a client is able to write either of the following:

- ``from kitchen import cabinet``
- ``from kitchen.containers import cabinet``

Both appear valid, and there's no hint to the client that ``cabinet`` is
only available from ``kitchen`` due to implementation details.
If backwards compatibility is valued, both imports must continue to work
even as the implementation is further revised, adding to the maintenance
burden.

Adding or removing external modules can also cause compatibility issues.
Consider the second example above. It seems unlikely that a client would
intentionally write code such as ``from haystack import re`` to access the
``re`` module. On the other hand, it's quite easy for clients to accidentally
write code accessing external modules through other modules without realizing
it, as in example:

.. code-block:: python

  # 're' imported into this file's namespace here
  from haystack import *

  # ...later, some code using re
  re.search(pattern, value)

