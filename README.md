# pidiff

`pidiff` - the Python interface diff tool

[![Build Status](https://circleci.com/gh/rohanpm/pidiff/tree/master.svg?style=svg)](https://circleci.com/gh/rohanpm/pidiff/tree/master)
[![Coverage Status](https://coveralls.io/repos/github/rohanpm/pidiff/badge.svg?branch=master)](https://coveralls.io/github/rohanpm/pidiff?branch=master)
[![Maintainability](https://api.codeclimate.com/v1/badges/64347682bb124ea1e1fb/maintainability)](https://codeclimate.com/github/rohanpm/pidiff/maintainability)

- [Documentation](https://pidiff.dev/)
- [Source](https://github.com/rohanpm/pidiff)
- [PyPI](https://pypi.python.org/pypi/pidiff)

`pidiff` is a tool to detect and report on API changes between multiple versions
of a Python module. It can be used as a testing tool to help a project follow
the [Semantic Versioning](https://semver.org/) spec.

## Examples

The `pidiff` command can install old and new package versions from PyPI and diff a
module between versions, failing if SemVer is not used appropriately.

Here's an example of a diff finding some problems:

````
$ pidiff more-executors==1.15.0 more-executors==1.16.0
more_executors/_wrap.py:6: N220 function added: flat_bind
more_executors/retry.py:46: N450 ExceptionRetryPolicy now accepts unlimited keyword arguments
more_executors/retry.py:46: B330 argument in ExceptionRetryPolicy can no longer be passed positionally: max_attempts (was position 0)
more_executors/retry.py:133: N450 RetryExecutor now accepts unlimited keyword arguments
more_executors/retry.py:133: B130 method removed: new_default

---------------------------------------------------------------------
Major API changes were found; inappropriate for 1.15.0 => 1.16.0
New version should be equal or greater than 2.0.0
````

Public API was removed without a major bump of the package version;
pidiff considers this an error and suggests the new minimum version
number which should be set to accept these changes.

Here's an example of a diff reporting a successful result:

````
$ pidiff more-executors==1.11.0 more-executors==1.12.0
more_executors/flat_map.py:0: N210 module added: flat_map
more_executors/_executors.py:84: N230 method added: with_flat_map

---------------------------------------------------------------------
Minor API changes were found; appropriate for 1.11.0 => 1.12.0
````

Public API was added; since there was a minor bump of the package version,
this is OK.

## License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
