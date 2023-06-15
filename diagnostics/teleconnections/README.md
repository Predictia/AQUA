# Teleconnections diagnostic

The folder contains jupyter-notebooks and python scripts in order to evaluate teleconnections in the DE_340 AQUA model evaluation framework.
The script are based on the `AQUA` framework.

## Python module

The python package is based on the `AQUA` framework.
A list of its dependencies can be found in the `environment.yml` file in the root of the repository.
Additionally, a specific list of the packages needed other that the framework environment can be found in the `env-teleconnections.yml` file, that can be used as well to create the `conda` environment needed to run the diagnostic.
The extra packages are:
- python-cdo (needed for tests only)
- cartopy (needed for plots only)

Teleconnections evaluation without plots can be run with the `AQUA` framework only.

The `teleconnections` environment installs the `AQUA` framework with the `pip` installation method, and the other packages with the `conda` installation method.
For this reason the `teleconnections` environment can have slightly different versions of the packages than the `AQUA` framework. 
Basic framework tests are run with github actions, in order to check that the `teleconnections` environment is compatible with the `AQUA` framework.

## Teleconnections available:

At the moment the following teleconnections are available:

- NAO (see NAO notebooks)
- ENSO (see ENSO notebooks)

These two teleconnections are evaluated with station-based indices or with the usage of regional means.
Other teleconnections can be configured by modifying the `teleconnections.yaml` file in the `config` folder.

See the documentation for more details on the teleconnections.

## Library files

- `cdotesting.py` contains function evaluating teleconnections with cdo bindings, in order to test the python libraries (see tests section).
- `index.py` contains functions for the direct evaluation of teleconnection indices. It is the core of the diagnostic.
- `plots.py` contains functions for the visualization of time series and maps for teleconnection diagnostic.
- `tools.py` contains generic functions that may be useful to the whole diagnostic.

## Tests

Tests are run with github actions, see `.github/workflows/teleconnections.yml` for details.
Tests make use of the `cdotesting.py` file, that contains functions evaluating teleconnections with cdo bindings.

## Notebooks

All notebooks are in the `notebooks` folder.

- `cdo_testing` contains an example of usage of the cdo bindings introduced in the `cdotesting.py` file.
- `NAO/ENSO` contain the respective teleconnections evaluated with the library methods from `index.py` and `plots.py`.

Notice that NAO and ENSO notebooks analyze ERA5 data.
There are extra notebooks for both the teleconnections with the analysis of nextGEMS cycle3 data.

## Create the teleconnections env

The `env-teleconnections.yml` file can be used to create the `conda` environment needed to run the diagnostic.

```bash
mamba env create -f env-teleconnections.yml # or conda
```

### Add kernel for DKRZ jupyterhub

Documentation on adding kernels: https://docs.dkrz.de/doc/software%26services/jupyterhub/kernels.html#use-your-own-kernel

After creating the environment, activate it and install the kernel:

'''bash
python -m ipykernel install --user --name teleconnections --display-name="teleconnections"
'''

### Lumi installation

`conda` is not available on Lumi, so the environment has to be created manually.

An installation tool similar to `lumi_installation.sh` has still to be written.