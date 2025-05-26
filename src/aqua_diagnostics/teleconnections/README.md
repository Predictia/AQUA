# Teleconnections diagnostic

Main authors: 
- Matteo Nurisso (CNR, m.nurisso@isac.cnr.it)

## Description

This diagnostic computes and plots:

- NAO index, regression and correlation maps
- ENSO index, regression and correlation maps

## Table of contents

- [Teleconnections diagnostic](#teleconnections-diagnostic)
  - [Description](#description)
  - [Table of contents](#table-of-contents)
  - [Installation instructions](#installation-instructions)
  - [Data requirements](#data-requirements)
  - [Examples](#examples)
- [Contributing](#contributing)

## Installation instructions

This diagnostic does not rely on any additional dependencies.
It is installed automatically when installing the AQUA environment.

## Data requirements

The diagnostic requires the following variable to compute the indexes:

- ``msl`` (Mean sea level pressure) for NAO
- ``tos`` (Sea surface temperature) for ENSO

These are the minimum requirements, but the diagnostic can be easily extended to other variables, since the regression and correlation maps can be done with every variable available in the dataset.
The names of the variables refers to the DestinE data governance, but the diagnostic can be easily adapted to other standards with the usage of the interface files.

Data should be preferably in the form of monthly means and it would be optimal for efficiency to have data on a grid with a resolution of 1°x1° (LRA format).
It is possible to initialize the class with asking to regrid the data.

Additionally, NCAR data with monthly values of NAO and ENSO indices are available in the `notebooks/diagnostics/teleconnections/data` folder.
These are used to compare the teleconnections with the observations in the example notebooks.

## Examples

The **AQUA/notebook/diagnostics/teleconnections** folder contains the following notebooks:

- **NAO.ipynb**:
  This notebook provides a brief overview of the NAO diagnostic.
- **ENSO.ipynb**:
  This notebook provides a brief overview of the ENSO diagnostic.

# Contributing

This diagnostic is maintained by Matteo Nurisso (@mnurisso, m.nurisso@isac.cnr.it).
Contributions are welcome, please open an issue or a pull request.
If you have any doubt or suggestion, please contact the AQUA team or Matteo Nurisso (@mnurisso, m.nurisso@isac.cnr.it).