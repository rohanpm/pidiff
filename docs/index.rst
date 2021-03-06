pidiff
======

The Python interface diff tool.

pidiff is a testing tool to help enforce the usage of
`Semantic Versioning <https://semver.org/>`_ on your Python projects.
It compares the public API provided by two versions of a pip-installable
package and produces a report of any changes detected, failing if changes
appear to violate SemVer.

.. ifconfig:: version

    This documentation was built from pidiff |version|.


Quick Start
-----------

Install the pidiff command from PyPI:

::

    pip install pidiff

Then run the pidiff command against two versions of a Python package.

If using the command as part of your development workflow, a typical use-case
would be to check the differences between the latest version of your package
released to PyPI, and the current version in your local git checkout:

::

    $ pidiff -r more-executors .
    more_executors/retry.py:133: N450 RetryExecutor now accepts unlimited keyword arguments
    more_executors/retry.py:133: B130 method removed: new_default
    more_executors/_wrap.py:6: N220 function added: flat_bind

    ---------------------------------------------------------------------
    Major API changes were found; inappropriate for 1.15.0 => 1.16.0
    New version should be equal or greater than 2.0.0


More information
----------------

.. toctree::
   :maxdepth: 2

   user-guide
   error-reference
   api-reference

* :ref:`genindex`
* :ref:`search`
