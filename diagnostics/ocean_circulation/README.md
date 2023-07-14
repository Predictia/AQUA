# Ocean Circulation diagnostic

Main authors: 
- Supriyo Ghosh (BSC, supryo.gosh@bsc.es)
- Pablo Ortega (BSC, pablo.ortega@bsc.es)

## Description

The current release of Ocean Circulation diagnostic includes climatological stratification profiles in regions of deep water formation and climatologies for the mixed layer depth.

## Table of Contents

- [Diagnostic of ocean circulation](#diagnostic-of-tropical-rainfalls)
  - [Description](#description)
  - [Table of Contents](#table-of-contents)
  - [Installation Instructions](#installation-instructions)
  - [Data requirements](#data-requirements)
  - [Examples](#examples)
  - [Contributing](#contributing)

## Installation Instructions

The diagnostic uses a standard aqua environment and requires no extra dependencies. 


To install of the diagnostic on Levante or Lumi, please follow the installation instructions in the main [README.md](https://github.com/oloapinivad/AQUA/blob/main/README.md) file of aqua.

## Data requirements  

The diagnostic requres a model data of 3D ocean potential temperature and practical salinity.

## Examples
The **notebook/** folder contains the notebook 
 **[ocean_circulation.ipynb](https://github.com/oloapinivad/AQUA/blob/main/diagnostics/ocean_circulation/notebooks/ocean_circulation.ipynb)**, that  demonstrates:
- the import of `ocean_circulation`module and configuration setup, 
- the primary diagnostic functions of `ocean_circulation` module, which compute and plot the mixed layer depth and climatological stratification profiles,
- the input data requierements, 
- the application of primary functions, and 
- the main sientific output, obtained by ocean circulation diagnostic.

## Contributing

The  ocean_circulation module is in a developing stage and will be significantly improved in the near future. If you have any suggestions, comments, or problems with its usage, please get in touch with the AQUA team, particulaty with Supriyo Ghosh (supryo.gosh@bsc.es) or Pablo Ortega (pablo.ortega@bsc.es).