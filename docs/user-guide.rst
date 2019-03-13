User Guide
==========


Command reference
-----------------

.. argparse::
    :module: pidiff._impl.command
    :func: argparser
    :prog: pidiff

    source1
        The most common forms of specifying a pip-installable package are supported,
        including:

        - latest version: ``mypkg``
        - a specific version or range: ``mypkg==1.0.0``, ``mypkg<2``
        - a local directory containing a ``setup.py``: ``~/src/mypkg``
