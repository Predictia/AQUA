# Diagnostic of tropical rainfalls

Main authors: 
- Natalia Nazarova (POLITO, natalia.nazarova@polito.it)

## Description

The tropical-rainfall diagnostic analyzes rainfall variability in the tropical zone and compares the climatological models' predictions with observations.  

The module comprises Python-implemented source files, an environment file, tests, demonstration files, and a command line interface. You can find a detailed description of the module in the aqua documentation. 

Below you can find a quick start to the tropical_rainfall diagnostic.

## Table of Contents

- [Diagnostic of tropical rainfalls](#diagnostic-of-tropical-rainfalls)
  - [Description](#description)
  - [Table of Contents](#table-of-contents)
  - [Installation Instructions](#installation-instructions)
  - [Data requirements](#data-requirements)
  - [Output](#output)
  - [Examples](#examples)
  - [Contributing](#contributing)

## Installation Instructions

The simplest method to install the Tropical Rainfall Diagnostic is through pip. Add the package to your list of pip dependencies:
```
pip install $AQUA/diagnostics/tropical_rainfall/
```
Alternatively, you can include the package in your Conda environment by adding the following line to your Conda environment file:
```
-e $AQUA/diagnostics/tropical_rainfall/
```
The Tropical Rainfall Diagnostic requires the installation of **fast_histogram** in addition to other dependencies. However, the installation of the Tropical Rainfall package is integrated into the Aqua package installation process.

For detailed installation instructions specific to environments like Levante or Lumi, please refer to the **Installation** sections in the README.md file of the AQUA package.


## Data requirements  

The following are the requirements for input climatological data:
Data must include the precipitation rate variable (**mtpr**) in a latitude and longitude grid. 

The diagnostic can be perrformed on the data of any spatial and time resolution. 

## Output 

All diagnostic outputs are provided in either NetCDF or PDF formats. Users can specify the output storage directory in the config file located at `$AQUA/diagnostics/tropical_rainfall/tropical_rainfall/config-tropical-rainfall.yml`, or directly during the initialization of the diagnostic:
```
diag = Tropical_Rainfall(path_to_netcdf = 'your/path/to/netcdf/', path_to_pdf = 'your/path/to/pdf/')
```



## Examples

The **notebook/** folder contains the following notebooks:
 - **([demo_for_lowres_data](https://github.com/DestinE-Climate-DT/AQUA/blob/main/diagnostics/tropical_rainfall/notebooks/demo_for_lowres_data.ipynb))**:

    The notebook demonstrates:
    - histogram comparison for different climate models,
    - the ability to merge a few separate plots into a single one, 
    - mean of tropical and global precipitation calculations for different climate models,
    - bias between climatological model and observations. 
 - **([functions_demo/histogram_calculation.ipynb](https://github.com/DestinE-Climate-DT/AQUA/blob/main/diagnostics/tropical_rainfall/notebooks/functions_demo/histogram_calculation.ipynb))**:

    The notebook demonstrates the major abilities of tropical rainfall diagnostic: 
    - initialization of an object of the diagnostic class, 
    - selection of the class attributes,  
    - calculation of the histograms in the form of xarray, 
    - saving the histograms in the storage,
    - and loading the histograms from storage.
 - **([functions_demo/histogram_plotting.ipynb](https://github.com/DestinE-Climate-DT/AQUA/blob/main/diagnostics/tropical_rainfall/notebooks/functions_demo/histogram_plotting.ipynb))**:

    The notebook demonstrates the abilities of the histogram plotting functions:
    - selection of the plot style: step line style, 2D smooth line style, and different color maps,
    - selection of the plot size, axes scales, 
    - saving plot into storage, 
    - plotting the counts, frequencies, and Probability density function (pdf) from the obtained histograms.
 - **([functions_demo/diagnostic_vs_streaming.ipynb](https://github.com/DestinE-Climate-DT/AQUA/blob/main/diagnostics/tropical_rainfall/notebooks/functions_demo/diagnostic_vs_streaming.ipynb))**:

    The notebook demonstrates the usage of diagnostic during the streaming mode:
    - saving the obtained histogram with the histogram into storage per each chunk of any data during the stream, 
    - loading all or multiple histograms from storage and merging them into a single histogram. 

 - **([functions_demo/data_attributes.ipynb](https://github.com/DestinE-Climate-DT/AQUA/blob/main/diagnostics/tropical_rainfall/notebooks/functions_demo/data_attributes.ipynb))**:

   The notebook demonstrates:
    - saving high-resolution data chunks with unique filenames incorporating 'time_band',
    - automatically updating 'time_band' when merging datasets,
    - and ensuring merged datasets in the filesystem reflect the accurate total time band.

## Contributing

The tropical_rainfall module is in a developing stage and will be significantly improved in the near future. If you have any suggestions, comments, or problems with its usage, please get in touch with the AQUA team or Natalia Nazarova (natalia.nazarova@polito.it).
