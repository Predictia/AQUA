# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

## [Unreleased]

Unreleased is the current development version.

## [v0.2-alpha]

This is the `AQUA` version that will be part of the Deliverable D340.7.1.2. This is mostly done by the inclusion of eleven diagnostics within the AQUA framework

- Added teleconnections diagnostic (#308, #309, #318, #333, #352)
- Added tropical cyclones diagnostic (#310, #345)
- Added performance indices diagnostic based on ECmean tool (#57, #327) 
- Added sea ice diagnostic (#353, #368)
- Adede global timeseries diagnostic (#358, #359)
- Added radiation analysis diagnostic (#301, #360)
- Added global mean bias diagnostic (#285, #371)
- Added SSH variability diagnostic (#367, #369)
- Added tropical rainfall diagnostic (#314)
- Added Ocean circulation diagnostic (#295)
- Added global ocean diagnositc (#164)
- Multiple fixes in the Reader (#316, #324, #334)
- Avoid time duplicated in the Reader (#357)
- Enabling autodoc for diagnostics (#330)
- Data access improvement on Levante, including new datasets (#332, #355, #321)
- Added a common environment file (#363)
- Support for Lumi installation (#315)
- Added the `changelog` file

## [v0.1-beta]

This is the `AQUA` version that will be part of the Deliverable D340.7.1.1.
This is mostly built on the `AQUA` `Reader` class which support for climate model data interpolation, spatial and temporal aggregation and conversion for a common GRIB-like data format.


- Low resolution archive documentation
- Fixed a bug in the `Gribber` class that was not reading the correct yaml catalogue file

## v0.1-alpha

This is the AQUA pre-release to be sent to internal reviewers. 
Documentations is completed and notebooks are working.

[unreleased]: https://github.com/oloapinivad/AQUA/compare/v0.2-alpha...HEAD
[v0.2-alfa]: https://github.com/oloapinivad/AQUA/compare/v0.1-beta...v0.2-alpha
[v0.1-beta]: https://github.com/oloapinivad/AQUA/compare/v0.1-alpha...v0.1-beta
