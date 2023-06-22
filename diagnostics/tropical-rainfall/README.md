# Diagnostic of tropical rainfalls

The main purpose of tropical rainfall diagnostic is to provide the xarray.Dataset, which contains histograms of precipitation for any climate model in tropical latitudes. 


## Description


The tropical rainfalls diagnostic proving for the user an excellent example of

* ...


## Table of Contents

* [Installation Instructions](#installation-instructions)

  - [Installation on Levante](#installation-on-levante)

  - [Installation on Lumi](#installation-on-lumi)

* [Diagnostic structure](#diagnostic-structure)

* [Code](#code)

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

## Diagnostic structure 

- **diagnostics/**: The root directory of the diagnostic.

  - **tropical-rainfall/**: contains the code of the diagnostic

    - **notebooks/**: contains notebooks with examples of how to use the diagnostic

    - **data/**: contains data for the tests if needed. Please do not commit large files to git. You can add data to the `.gitignore` file if needed. Make always use of the `Reader` class and functions available in the framework to load data. If you need to add data to the catalogue, please contact the AQUA team.

    - **env-dummy.yml**: contains the dependencies for the diagnostic. It is used to create a conda environment for the diagnostic. Diagnostics should be developed in separate environments to avoid conflicts between diagnostics that may need different python packages. Always check that the diagnostic works with the latest version of the framework and eventually update the dependencies in the `env-dummy.yml` file. (If you have suggestions on how to improve this, please let us know.s)

- **tests/**

  - **tropical-rainfall/**: contains tests for the diagnostic. Please add tests for all the functions you add to the diagnostic. Please load data that are needed for the tests not in the git. You may need to add data to the catalogue for the `ci` machine. If you need to add data to this catalogue, please contact the AQUA team. Tests run with a github action when you push to the repository in a pull request to the main branch. Note that the workflow file is in the `.github` folder. Modify it accordingly to your diagnostic and uncomment the lines to run the tests when you are ready. Please keep in mind that the suggested way to proceed is based on the creation of a `@pytest.mark.tropical_rainfall` marker so that you can select only the test that you need in the workflow (see the workflow example). This marker has to be added in the `pytest.ini` file.  



- **docs/sphinx/sorce/diagnostics/tropical-rainfall.rts**: contains the documentation for the diagnostic. Please add documentation for all the functions you add to the diagnostic. The documentation is built with sphinx.
Read the documentation for a detailed description of the diagnostic and diagnostic usage.

## Code

The module of tropical rainfall diagnostic is `tropical_rainfall_class.py`. 


## Data requirements  



## Examples

The **notebook/** folder contains the following notebooks:
 - **ICON_histogram_calculation.ipynb**: 

    The notebook demonstrates the major abilities of tropical rainfall diagnostic: 
    - initialization of an object of the diagnostic class, 
    - selection of the class attributes,  
    - calculation of the histograms in the form of xarray, 
    - saving the histograms in the storage,
    - and loading the histograms from storage.
 - **ICON_histogram_plotting.ipynb**:

    The notebook demonstrates the abilities of the histogram plotting functions:
    - selection of the plot style: step line style, 2D smooth line style, and different color maps,
    - selection of the plot size, axes scales, 
    - saving plot into storage, 
    - plotting the counts, frequencies, and Probability density function (pdf) from the obtained histograms.
 - **diagnostic_vs_streaming.ipynb**:

    The notebook demonstrates the usage of diagnostic during the streaming mode:
    - saving the obtained histogram with the histogram into storage per each chunk of any data during the stream, 
    - loading all or multiple histograms from storage and merging them into a single histogram. 

 - **histogram_comparison.ipynb**:

    The notebook demonstrates:
    - a simple comparison of obtained histograms for different climate models, 
    - ability to merge a few separate plots into a single one. 

 - **diagnostic_example_for_2t.ipynb**:
    The notebook illustrates that:
    - The tropical precipitation diagnostic can be applied to any climate model variable. 



## Contributing

Include your contact information or any official channels (such as email, GitHub profile) through which users can reach out to you for support, questions, or feedback.




