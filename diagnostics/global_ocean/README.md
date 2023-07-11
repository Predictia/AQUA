# Global Ocean diagnostic

Main authors: 
- Supriyo Ghosh (BSC, supryo.gosh@bsc.es)
- Pablo Ortega (BSC, pablo.ortega@bsc.es)

# Description

The Global Ocean diagnostic allows tracking the evolution and trends of temperature and salinity in the global and other regional oceans, using a battery of hovmöller figures, time series plots, and maps of regional and temporal trends at different ocean depths.

## Table of Contents

- [Diagnostic of global ocean](#diagnostic-of-tropical-rainfalls)
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

The **notebook/** folder contains the notebook **[global_ocean.ipynb](https://github.com/oloapinivad/AQUA/blob/main/diagnostics/global_ocean/notebooks/global_ocean.ipynb)**, which demonstrates:
- the import of `global_ocean`module and configuration setup, 
- the major functions of the `global_ocean` module, which produce hovmollers in-depth and time, time-series of yearly potential ocean temperature and practical salinity, 
- the data requierements, 
- demonstrating the usage of primary functions, and 
- the main scientific output obtained by global ocean diagnostic.

## Contributing

The global_ocean module is currently undergoing development and will soon be substantially enhanced. Please get in touch with the AQUA team, specifically Supriyo Ghosh (supryo.gosh@bsc.es) or Pablo Ortega (pablo.ortega@bsc.es), if you have any suggestions, remarks, or issues regarding its use.


