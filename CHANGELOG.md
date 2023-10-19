# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
from version 1.0.0 onwards.

## [Unreleased]

- n/a

## [1.7.1] - 2023-10-20

### Fixed

- Fixed compatibility with `astroid >= 3.0`.

## [1.7.0] - 2021-08-26

### Fixed

- Version detection of the tested modules is now more accurate in some cases,
  via usage of `importlib.metadata`.

### Changed

- Now requires python 3.8 or later.

## [1.6.0] - 2020-07-01

### Fixed

- Fixed handling of `--requirement`, `--constraint` when relative paths are
  provided

### Changed

- Duplicate log messages are no longer generated when a single API change
  has been exposed via multiple references (example: adding a method to a class which
  has been subclassed, meaning the new method is available on both the
  parent and child class(es)).

  Using `--full-symbol-names` will continue to log all references to an
  API change.

## [1.5.0] - 2020-06-27

### Added

- ``--gen-version`` option was introduced for programmatic use. This option can be
  used to implement automated version bumps for a project.
- ``--pip-args`` and related options were introduced to support passing
  additional arguments to pip.

### Fixed

- Removed usage of functions deprecated in python-semver 2.10

## [1.4.0] - 2019-08-19

### Changed

- The `pidiff` command now stores virtual environments under the
  `XDG_CACHE_HOME` directory by default, rather than a `.pidiff` directory.

## [1.3.0] - 2019-06-05

### Added

- New check `added-argument-default`: pidiff now reports when an existing argument
  has a default value introduced

## [1.2.0] - 2019-05-25

### Fixed

- When the target module version of a diff is an initial development version `0.y.z`,
  pidiff now considers that any and all API changes are appropriate, per item #4
  in the SemVer spec.

## [1.1.0] - 2019-05-19

### Added

- pidiff now parses AST to find more properties on classes

## 1.0.0 - 2019-03-17

- Initial supported release


[Unreleased]: https://github.com/rohanpm/pidiff/compare/v1.7.1..HEAD
[1.7.1]: https://github.com/rohanpm/pidiff/compare/v1.7.0..v1.7.1
[1.7.0]: https://github.com/rohanpm/pidiff/compare/v1.6.0..v1.7.0
[1.6.0]: https://github.com/rohanpm/pidiff/compare/v1.5.0..v1.6.0
[1.5.0]: https://github.com/rohanpm/pidiff/compare/v1.4.0..v1.5.0
[1.4.0]: https://github.com/rohanpm/pidiff/compare/v1.3.0..v1.4.0
[1.3.0]: https://github.com/rohanpm/pidiff/compare/v1.2.0..v1.3.0
[1.2.0]: https://github.com/rohanpm/pidiff/compare/v1.1.0..v1.2.0
[1.1.0]: https://github.com/rohanpm/pidiff/compare/v1.0.0..v1.1.0
