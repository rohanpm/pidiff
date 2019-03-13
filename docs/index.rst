pidiff
======

The Python interface diff tool

* `Documentation <https://rohanpm.github.io/pidiff/>`_
* `Source <https://github.com/rohanpm/pidiff>`_
* `PyPI <https://pypi.python.org/pypi/pidiff>`_

pidiff is a testing tool to help enforce the usage of
`Semantic Versioning <https://semver.org/>`_ on your Python projects.
It compares the public API provided by two versions of a pip-installable
package and produces a report of any changes detected, failing if changes
appear to violate SemVer.

.. ifconfig:: version

    This documentation was built from pidiff |version|.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   user-guide


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
    more_executors/_executors.py:49: D200 object added: more_executors.Executors.flat_bind
    more_executors/retry.py:46: D100 object removed: more_executors.retry.ExceptionRetryPolicy.new_default
    more_executors/retry.py:133: D100 object removed: more_executors.retry.RetryExecutor.new_default

    ---------------------------------------------------------------------
    Major API changes were found; inappropriate for 1.15.0 => 1.16.0
    New version should be equal or greater than 2.0.0


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
