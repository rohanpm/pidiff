User Guide
==========


The pidiff command
------------------

.. argparse::
    :module: pidiff._impl.command
    :func: argparser
    :prog: pidiff
    :nodefaultconst:
    :nodescription:

    The ``pidiff`` command compares two versions of a Python package
    and produces a report on API differences.

    source1
        The most common forms of specifying a pip-installable package are supported,
        including:

        - latest version: ``mypkg``
        - a specific version or range: ``mypkg==1.0.0``, ``mypkg<2``
        - a local directory containing a ``setup.py``: ``~/src/mypkg``


Output format
.............

The ``pidiff`` command produces output as in the following example:

::

    $ pidiff more-executors==1.15.0 more-executors==1.16.0
    more_executors/_executors.py:49: N230 method added: flat_bind
    more_executors/retry.py:46: N450 ExceptionRetryPolicy now accepts unlimited keyword arguments
    more_executors/retry.py:46: B330 argument in ExceptionRetryPolicy can no longer be passed positionally: max_attempts (was position 0)
    more_executors/retry.py:133: N450 RetryExecutor now accepts unlimited keyword arguments
    more_executors/retry.py:133: B130 method removed: new_default
    more_executors/_wrap.py:6: N220 function added: flat_bind

    ---------------------------------------------------------------------
    Major API changes were found; inappropriate for 1.15.0 => 1.16.0
    New version should be equal or greater than 2.0.0

For each change found, a message is produced with:

    **<file>:<line>**
        Approximate location of the added/removed/changed object.

        Note that this is the location where the related object is defined,
        which may not be in the same file where the object is exported as
        public API.

    **error code**
        Each type of error is associated with an error code.
        Error codes are one of:

        **Nxxx**
            *New* backwards-compatible functionality. New classes,
            objects, functions or arguments are available to clients.
            The package minor version must be increased.

        **Bxxx**
            *Breaking* changes. Classes, objects, functions or arguments
            were removed or changed in such a way that clients written against
            the old package version may be broken when used against the new
            version. The package major version must be increased.

    **summary**
        A summary explaining why the diff passed or failed.

        If the diff fails, a new version number will be suggested for the
        package, where possible.


Exit codes
..........

The ``pidiff`` command uses the following exit codes:

    0
        Either no differences were found, or all differences
        are appropriate for old and new package versions.

    99
        Breaking API changes were found, and this is
        inappropriate for the old and new package versions;
        the major version should be bumped.

    88
        New functionality was found, and this is inappropriate
        for the old and new package versions; the minor version
        should be bumped.

    *other non-zero*
        An error occurred.


Configuring checks
------------------

By default, ``pidiff`` enables all checks.

Individual checks may be explicitly disabled or enabled either using
the ``--disable``, ``--enable`` command-line options, or using a settings
file.

``pidiff`` will look for settings in these files, in the current directory
and any parent directories:

- ``pidiff.ini``
- ``tox.ini``
- ``setup.cfg``

Settings should be placed under a ``[pidiff]`` section. Checks may be enabled
or disabled as in the following example:

::

    [pidiff]
    # list of checks to enable
    enable=
        N450
        B330

    # list of checks to disable
    disable=
        B130

The ``enable`` setting and command-line argument takes precedence over
``disable``.


What is "public API"?
---------------------

Roughly, the tool's concept of "public API" is: any object reachable from
any modules underneath your package's entry point, with a name not
beginning with ``_``.

A more complete description of the method used to enumerate public API follows.

- First, the ``module_name`` given to the ``pidiff`` command is imported (or,
  if omitted, the module to import is detected from the package's top_level.txt
  metadata).

- All submodules of that module are also imported, recursively, ignoring any
  modules whose name begins with ``_``.

- All modules imported by the above process are enumerated with :meth:`dir()`
  to find available objects; those objects themselves are enumerated with
  :meth:`dir()` to find child objects; and so on, recursively.  Processing
  stops for any objects whose name begins with ``_`` or whose location is
  not underneath the directory containing the API entry point.


Caveats and limitations
-----------------------

- Python 2.x is not supported.

- It must be possible to import the API to be checked from within the same
  Python interpreter used for the ``pidiff`` command.

- ``pidiff`` doesn't check the return values of functions and methods.

- ``pidiff`` is designed for pure Python modules only and is not expected to
  work for native extensions.
