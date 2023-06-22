# Dummy diagnostic

This is a dummy diagnostic that does nothing.
It is meant to be used as a template for new diagnostics.

## Description

Concise overview that explains the purpose, key features, and benefits of your diagnostics.

Below you can find the example:

The dummy-diagnostic proving for the user an excellent example of

* how to organize the diagnostic structure,
* how to maintain the class and functions,
* how to write the docstrings,
* how to compose the primary sphinx documentation,
* how to organize the notebooks, 
* how to implement simple pytest, and 
* how to write the readme file.

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

To install this diagnostic you can use conda.
The `environment.yml` file contains the dependencies for this diagnostic.
It is located in `AQUA/diagnostics/dummy-diagnostic/env-dummy.yml`.

To install the diagnostic in a new conda environment run:

```bash
conda env create -f env-dummy.yml
```

To install the diagnostic in an existing conda environment run:

```bash
conda env update -f env-dummy.yml
```

To activate the environment run:

```bash
conda activate dummy-diagnostic
```

or the name of the environment you chose to update.

The diagnostic environment is compatible with python 3.9 and 3.10 and with the AQUA framework.
Different diagnostic environments may be not compatible with each other.
If you want to use multiple diagnostics at the same time, it is recommended to use the different environments for each of them.

### Installation on Lumi 

## Diagnostic structure 

- **diagnostics/**: The root directory of the diagnostic.

  - **dummy-diagnostic/**: contains the code of the diagnostic

    - **notebooks/**: contains notebooks with examples of how to use the diagnostic

    - **data/**: contains data for the tests if needed. Please do not commit large files to git. You can add data to the `.gitignore` file if needed. Make always use of the `Reader` class and functions available in the framework to load data. If you need to add data to the catalogue, please contact the AQUA team.

    - **env-dummy.yml**: contains the dependencies for the diagnostic. It is used to create a conda environment for the diagnostic. Diagnostics should be developed in separate environments to avoid conflicts between diagnostics that may need different python packages. Always check that the diagnostic works with the latest version of the framework and eventually update the dependencies in the `env-dummy.yml` file. (If you have suggestions on how to improve this, please let us know.s)

- **tests/**

  - **dummy-diagnostic/**: contains tests for the diagnostic. Please add tests for all the functions you add to the diagnostic. Please load data that are needed for the tests not in the git. You may need to add data to the catalogue for the `ci` machine. If you need to add data to this catalogue, please contact the AQUA team. Tests run with a github action when you push to the repository in a pull request to the main branch. Note that the workflow file is in the `.github` folder. Modify it accordingly to your diagnostic and uncomment the lines to run the tests when you are ready. Please keep in mind that the suggested way to proceed is based on the creation of a `@pytest.mark.yourdiag` marker so that you can select only the test that you need in the workflow (see the workflow example). This marker has to be added in the `pytest.ini` file.  



- **docs/sphinx/sorce/diagnostics/dummy-diagnostic.rts**: contains the documentation for the diagnostic. Please add documentation for all the functions you add to the diagnostic. The documentation is built with sphinx.

## Code

Please add docstrings to all the functions you add to the diagnostic.
You can find an example of how to write the docstrings in the `dummy_class.py` file. 

Make sure that the code passes the `flake8` checks.
Take advantage as much as possible of the functions available in the framework. 

If new data or functions that you think may be useful for other diagnostics are needed, please contact the AQUA team. It may be added to the framework.


## Data requirements  

Please specify if your diagnostic can only be performed on data with a particular time or space grid. 

For instance, "The dummy diagnostic can only be performed on regridded data" or "The diagnostic can only be performed on monthly data".

## Examples

The notebooks demonstrate your diagnostic's capabilities, help users understand the potential applications, and inspire them to use it.
Please note that notebooks may load data from the DKRZ cluster, so they may not work outside of it.

The **notebook/** folder contains the following notebooks:

 - **Save_data_to_storage.ipynb**: 

    The notebook demonstrates the major abilities of dummy diagnostic: 
    - initialization of an object of the diagnostic class, 
    - selection of the class attributes,  
    - saving the data in the storage, and 
    - loading the data from storage.

 - **Save_figure_to_storage.ipynb**:

    The notebook demonstrates the abilities of the histogram plotting functions:
    - selection of the plot style,
    - selection of the plot size, axes scales, and 
    - saving plot into storage.


## Contributing

Include your contact information or any official channels (such as email, GitHub profile) through which users can reach out to you for support, questions, or feedback.

