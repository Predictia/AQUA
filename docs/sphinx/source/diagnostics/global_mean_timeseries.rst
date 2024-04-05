.. _global_mean_timeseries:

Global mean time series
=======================

Description
-----------

The diagnostic is composed of three main functionalities that are implemented as three classes:

* **Timeseries**: a class that computes the global mean time series of a given variable or formula for a given model or list of models. Comparison with a reference dataset is also possible.
* **GregoryPlot**: a class that computes the Gregory-like plot for a given model or list of models. Comparison with a reference dataset is also possible.
* **SeasonalCycle**: a class that computes the seasonal cycle of a given variable or formula for a given model or list of models. Comparison with a reference dataset is also possible.


Structure
-----------

* ``README.md``: a readme file which contains some technical information on how to install the diagnostic and its environment.
* ``pyproject.toml``: a configuration file for the project. This is inteded to be used when installing the AQUA environment.
* ``global_time_series``: a subdirectory which contains the diagnostic source code. Each class is implemented in a separate file.
* ``notebooks``: a subdirectory which contains Jupyter notebooks that demonstrate the diagnostic functionalities.
* ``cli``: a subdirectory which contains the command line interface for the diagnostic.

Input variables
---------------

The diagnostic requires the variables that the user wants to analyse.
For the Gregory-like plot, the following variables are required:

* ``2t`` (2 metre temperature, GRIB paramid 167)
* ``mtnlwrf`` (Mean top net long-wave radiation flux, GRIB paramid 235040)
* ``mtnswrf`` (Mean top net short-wave radiation flux, GRIB paramid 235039)

CLI usage
---------

The diagnostic can be run from the command line interface (CLI) by running the following command:

```
cd $AQUA/diagnostics/global_time_series/cli
python cli_global_time_series.py --config_file <path_to_config_file>
```

The configuration file is a YAML file that contains the following information:

* ``models``: a list of models to analyse
* ``outputdir``: the directory where the output files will be saved
* ``timeseries``: a list of variables to compute the global mean time series
* ``gregory``: a block that contains the variables required for the Gregory plot
* ``seasonal_cycle``: a list of variables to compute the seasonal cycle

Three configuration files are provided and run when executing the aqua-analysis (see :ref:`aqua_analysis`)

Output
------

The diagnostic producestwo plots:

* ``timeseries.png``  A comparison of ICON and IFS global mean temperature
* ``gregory.png``     A Gregory-like plot to analyse model drift in ICON

and two data files:

* ``icon_2t_mean.nc`` Data for Gregory-like plot to analyse model drift in ICON
* ``ifs_2t_mean.nc``  Data for Gregory-like plot to analyse model drift in IFS

Observations
------------

The diagnostic has an optional dependence on the ERA5 reanalysis dataset.

Example Plot(s)
---------------

.. figure:: figures/global_time_series_gregory.png

    Gregory plot of IFS-NEMO historical-1990 and ssp370 simulations.
    The left panel represents the monthly Gregory plot, while on the right the annual Gregory plot is shown.
    The start and end point of the Gregory plot are indicated by the green and red arrows, respectively.
    In the annual Gregory plot a band representing the 2 sigma confidence interval is shown in green.
    This is evaluated with ERA5 data (1980-2010) for the 2m temperature and with CERES data (2000-2020) for the Net radiation TOA.

.. figure:: figures/global_time_series_timeseries.png

    Global mean temperature time series of IFS-NEMO historical-1990 and comparison with ERA5.
    Both monthly and annual timeseries are shown. A 2 sigma confidence interval is evaluated for ERA5 data (1990-2020).

.. figure:: figures/global_time_series_seasonalcycle.png

    Seasonal cycle of the global mean temperature of IFS-NEMO historical-1990 and comparison with ERA5.
    The 2 sigma confidence interval is evaluated for ERA5 data (1990-2020).

Available demo notebooks
------------------------

Notebooks are stored in diagnostics/global_time_series/notebooks

* `global_time_series.ipynb <https://github.com/oloapinivad/DestinE-Climate-DT/blob/main/diagnostics/global_time_series/notebooks/global_time_series.ipynb>`_
* `seasonal_cycles.ipynb <https://github.com/oloapinivad/DestinE-Climate-DT/blob/main/diagnostics/global_time_series/notebooks/seasonal_cycles.ipynb>`_

Detailed API
------------

This section provides a detailed reference for the Application Programming Interface (API) of the "global_mean_timeseries" diagnostic,
produced from the diagnostic function docstrings.

.. automodule:: global_time_series
    :members:
    :undoc-members:
    :show-inheritance:
