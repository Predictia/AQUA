# Diagnostic of tropical rainfalls

The tropical-rainfall diagnostic analyzes rainfall variability in the tropical zone and compares the climatological models' predictions with observations.  The mean precipitation variability is an excellent indicator of the accuracy of climatological simulations.



## Description

The module comprises Python-implemented source files, an environment file, tests, demonstration files, and a command line interface. You can find a detailed description of the module in the aqua documentation. 

Below you can find a quick start to the tropical_rainfall module. 

## Table of Contents

* [Installation Instructions](#installation-instructions)

  - [Installation on Levante](#installation-on-levante)

  - [Installation on Lumi](#installation-on-lumi)

* [Data requirements](#data-requirements)

* [Examples](#examples)


* [Contributing](#contributing)

## Installation Instructions

Clearly explain how to install and set up your project. Include any dependencies, system requirements, or environment configurations that users should be aware of.

### Installation on Levante


`env-tropical-rainfall.yml` file contains the minimal requirement for tropical diagnostic: 
 - dask_histogram. 


We need to install all requirements for tropical diagnostic with `pip` only. Since such dependencies are not presented in the environment of the main aqua module, we can merge the `env-tropical-rainfall.yml` and standard aqua `environment.yml` files without negative consequences, i.e.without potential conflict in the requirements:

```
diagnostic_dir=$(pwd)

conda install  conda-merge 

cd ../..

conda-merge environment.yml  $diagnostic_dir/env-tropical-rainfall.yml > $diagnostic_dir/merged.yml

conda env create -f $diagnostic_dir/merged.yml
```


### Installation on Lumi 




## Data requirements  

The following are the requirements for input climatological data:
Data must include the precipitation rate variable (**tprate**) in a latitude and longitude grid. 

## Examples

The **notebook/** folder contains the following notebooks:
 - **histogram_calculation.ipynb**: 

    The notebook demonstrates the major abilities of tropical rainfall diagnostic: 
    - initialization of an object of the diagnostic class, 
    - selection of the class attributes,  
    - calculation of the histograms in the form of xarray, 
    - saving the histograms in the storage,
    - and loading the histograms from storage.
 - **histogram_plotting.ipynb**:

    The notebook demonstrates the abilities of the histogram plotting functions:
    - selection of the plot style: step line style, 2D smooth line style, and different color maps,
    - selection of the plot size, axes scales, 
    - saving plot into storage, 
    - plotting the counts, frequencies, and Probability density function (pdf) from the obtained histograms.
 - **diagnostic_vs_streaming.ipynb**:

    The notebook demonstrates the usage of diagnostic during the streaming mode:
    - saving the obtained histogram with the histogram into storage per each chunk of any data during the stream, 
    - loading all or multiple histograms from storage and merging them into a single histogram. 

 - **comparison_of_lowres_models.ipynb**:

    The notebook demonstrates:
    - histogram comparison for different climate models,
    - the ability to merge a few separate plots into a single one, 
    - mean of tropical and global precipitation calculations for different climate models,
    - bias between climatological model and observations. 


## Contributing

The tropical_rainfall module is in a developing stage and will be significantly improved in the near future. If you have any suggestions, comments, or problems with its usage, please get in touch with the AQUA team. 



