# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

## [Unreleased]

Unreleased is the current development version.
It is stored in the `dev` branch.
When becoming stable, it will be merged into the `main` branch and developers of different diagnostics
will be able to check here what has changed.

### Added

- Added the `changelog` file

## [v0.1-beta]

This is the `AQUA` version that will be part of the Deliverable D340.7.1.1.
This is mostly built on the `AQUA` `Reader` class which support for climate model data interpolation, spatial and temporal aggregation and conversion for a common GRIB-like data format.

### Added

- Low resolution archive documentation

### Fixed

- Fixed a bug in the `Gribber` class that was not reading the correct yaml catalogue file

## v0.1-alpha

This is the AQUA pre-release to be sent to internal reviewers. 
Documentations is completed and notebooks are working.

[unreleased]: https://github.com/oloapinivad/AQUA/compare/HEAD...dev
[v0.1-beta]: https://github.com/oloapinivad/AQUA/compare/v0.1-alpha...v0.1-beta

## Template

This is a template for the changelog.
Introduce the categories that you need and remove the ones that you don't need in the changelog.

### Added

- Added a new feature

### Changed

- Changed a feature

### Removed

- Removed a feature

### Fixed

- Fixed a bug

### Security

- Fixed a security issue

### Deprecated

- Deprecated a feature

### Breaking

- Breaking changes

### Other

- Other changes
