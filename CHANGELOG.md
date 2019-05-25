# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
from version 1.0.0 onwards.

## [Unreleased]

- n/a

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


[Unreleased]: https://github.com/rohanpm/pidiff/compare/v1.2.0..HEAD
[1.2.0]: https://github.com/rohanpm/pidiff/compare/v1.1.0..v1.2.0
[1.1.0]: https://github.com/rohanpm/pidiff/compare/v1.0.0..v1.1.0
