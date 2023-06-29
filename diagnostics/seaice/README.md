# Sea ice diagnostics


### Folders

- `diagnostics/seaice`: contains the code of the diagnostics (see the `seaice_class.py`)
- `diagnostics/seaice/notebooks`: contains notebooks with examples of how to use the diagnostics
- `docs/sphinx/source/seaice/seaice-diagnostic.rts`: contains the documentation for the diagnostic. The documentation is built with sphinx.

### Code

Please add docstrings to all the functions you add to the diagnostic.
Make sure that the code passes the `flake8` checks.
Take advantage as much as possible of the functions available in the framework. If new data or functions that you think may be useful for other diagnostics are needed, please contact the AQUA team. It may be added to the framework.

## Installation

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

## Examples

The `notebooks` folder contains notebooks with examples of how to use the diagnostic and its main functions.
Please note that notebooks may load data from the DKRZ cluster, so they may not work outside of it.
