Tropical Cyclones detection, tracking and zoom in diagnostic
==================================================================

Description
-----------

This diagnostic package provides a tool to detect tropical cyclones (TCs) and compute their trajectory. Moreover it allows one to save selected variables
in the vicinity of the TCs centres.
Please write here in a clear and concise manner what the diagnostic is about 
and what it is supposed to be doing and the motivation behind it (i.e. which phenomenon or physical process 
is diagnosed and why it is important in the context of the analysis of high-resulution climate simulations).
In case the diagnostic is based on some already published material it is strongly 
recommended to include references to the inherent literature (we have a reference list below).


Structure
-----------

The dummy diagnostic follows a class structure and consists of the files:

* `notebooks/tropical_cyclones`: a python notebook which provides an example use of the TCs diagnostic, including the TCs class initialisation,
                                 a wrapper function which calls the DetectNodes and StitchNodes functions from tempest-extremes (which now are implemented
                                 as methods of the TCs class) and saves the data in the vicinity of the detected TCs at each time step and for the TCs tracks
                                 in a considered time interval. Finally some plotting functions are included to plot some selected variables at a few time steps
                                 and the TCs tracks in a particular period.
* `functions_TCs.py`: a python file which contains some functions (external to the tropical cyclones class) to analyse the output text files
                      produced by running the tempest-extremes methods DetectNodes and StitchNodes. Adapted from from the cymep repository
                      by Colin Zarzycki (https://github.com/zarzycki/cymep).
* `env-dummy.yml`: a yaml file with the required dependencies for the dummy diagnostic;
* `notebooks/dummy.ipynb`: an ipython notebook which uses the dymmy class and its methods;
* `README.md` : a readme file which contains some tecnical information on how to install the dummy diagnostic and its environment. 

Input variables
---------------

* `msl`     (Mean sea level pressure, GRIB paramid 151)
* `z`       (Geopotential height, GRIB paramid 129 at 300 and 500 hPa and at the surface (orography))
* `10u`     (2m zonal wind, GRIB pramid 165)
* `10v`     (2m meridional wind, GRIB pramid 166)

Output 
------

Here is a list of files produced by the tropical cyclones diagnostic:

* tempest_output_yyyymmddThh.txt:            text files produced by Tempest DetectNodes with TCs centres coordinates and maximum wind at each time step; 
* tempest_track_yyyymmddThh-yyyymmddThh.txt: text files produced by Tempest StitchNodes with TCs centres coordinates and maximum wind; 
                                             for each TC trajectory (i.e. after tracking is applied); 
* TC_var_yyyymmddThh.nc:                     netcdf files with selected variables in the vicinity of each TC centre detected at each time step
* tempest_track_yyyymmddThh-yyyymmddThh.nc:  netcdf files with selected variables in the vicinity of each TC centre following TCs trajectories 
                                             (includes time dimension, yyyymmddThh-yyyymmddThh states the start-end period considered)

Example of outpud variables saved in the vicinity of TCs centres are:

* `msl`     (Mean sea level pressure, GRIB paramid 151)
* `10u`     (10m zonal wind, GRIB pramid 165)
* `10v`     (10m meridional wind, GRIB pramid 166)
* `pr`      (Total precipitation, GRIB pramid 228)
* `10fg`    (10m wind gust since the last postprocessing, GRIB pramid 49)

Figures include output variables in the vicinity of TCs centres at various time steps (useful to compare wind intensity, precipitation distribution
and intensity between original resolution and a coarser resolution or with observations) and a figure with all the TCs tracks in the period considered.

Methods used
------------

Examples from the DummyDiagnostic class contained in the dummy_class.py file:

* "DummyDiagnostic": the Dummy diagnostic class;
* "retrieve": method to retrieve the data from the Reader class;
* "fldmean": method to compute the field mean of the retrieved data;
* "multiplication": method to compute the multiplication of the retrieved data. 
                    It is an example of method that uses of external functions of the module dummy_func

Note that it is important to add docstrings to each method.
We are following `Google-style docstring <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html>`_

.. note::
    Please note that there is no need to list all the methods used, but the most important which are exposed to the users should be presented

Functions used
--------------

Example of functions contained in the dummy_func.py file:

* "dummy_func": dummy function used in the dummy class.

Note that it is important to add docstrings to each function.
We are following `Google-style docstring <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html>`_

.. note::
    Please note that there is no need to list all the methods used, but the most important which are exposed to the users should be presented

Observations
------------

If relevant, list the observational datasets used by this diagnostic (e.g. for validation/comparison). Some examples are ERA5 reanalysis, CERES, MSWEP etc...

References
----------

* E. Empty, D. Dummy et al. (2023) The art of saying nothing. Emptyness, 1: 0-1. `DOI <http://doi.org/00.0000/e-00000-000.xxxx>`_


Example Plot(s)
---------------

.. figure:: figures/dummy-diagnostic1.png
    :width: 10cm

    An illustration of the big void left by this diagnostic

Available demo notebooks
------------------------

Notebooks are stored in diagnostics/dummy-diagnostic/notebooks

* `dummy_class_readerwrapper.ipynb <https://github.com/oloapinivad/AQUA/blob/main/diagnostics/dummy/notebooks/dummy_class_readerwrapper.ipynb>`_
* `dummy_class_timeband.ipynb <https://github.com/oloapinivad/AQUA/blob/main/diagnostics/dummy/notebooks/dummy_class_timeband.ipynb>`_
        
Detailed API
------------

This section provides a detailed reference for the Application Programming Interface (API) of the "dummy" diagnostic,
produced from the diagnostic function docstrings.

.. automodule:: dummy
    :members:
    :undoc-members:
    :show-inheritance:
