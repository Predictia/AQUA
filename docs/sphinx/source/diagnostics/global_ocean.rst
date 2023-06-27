Global Ocean
================

Description
-----------



Structure
-----------

The global_ocean diagnostic follows a class structure and consists of the files:

* `global_ocean_class.py`: a python file in which the global_oceanDiagnostic class constructor and the other class methods are included;
* `global_ocean_global_ocean_func.py`: a python file which contains functions that are called and used in the global_ocean class;
* `env-global_ocean.yml`: a yaml file with the required dependencies for the global_ocean diagnostic;
* `notebooks/global_ocean_class_global_mean.ipynb`: an ipython notebook which uses the dymmy class and its methods;
* `notebooks/global_ocean_class_basin_T_S_means.ipynb`: an ipython notebook which uses the dymmy class and its methods;
* `README.md` : a readme file which contains some tecnical information on how to install the global_ocean diagnostic and its environment. 

Input variables example
------------------------

* `tprate` (total precipitation rate, GRIB paramid 260048)
* `2t`     (2 metre temperature, GRIB pramid 167)

Output 
------

List here types of files/datasets produced by the diagnostic

Methods used
------------

Examples from the GlobaloOceanDiagnostic class contained in the global_ocean_class.py file:

* "global_oceanDiagnostic": the global_ocean diagnostic class;
* "retrieve": method to retrieve the data from the Reader class;
* "fldmean": method to compute the field mean of the retrieved data;
* "multiplication": method to compute the multiplication of the retrieved data. 
                    It is an example of method that uses of external functions of the module global_ocean_func

...

Functions used
--------------

Example of functions contained in the global_ocean_func.py file:

* "global_ocean_func": global_ocean function used in the global_ocean class.

Note that it is important to add docstrings to each method or function.

Observations
------------

If relevant, list the observational datasets used by this diagnostic (e.g. for validation/comparison). Some examples are ERA5 reanalysis, CERES, MSWEP etc...

References
----------

* E. Empty, D. global_ocean et al. (2023) The art of saying nothing. Emptyness, 1: 0-1. `DOI <http://doi.org/00.0000/e-00000-000.xxxx>`_


Example Plot(s)
---------------

.. figure:: figures/global_ocean-diagnostic1.png
    :width: 10cm

    An illustration of the big void left by this diagnostic

Available demo notebooks
------------------------

Notebooks are stored in diagnostics/global_oceandiagnostic/notebooks

* `global_ocean.ipynb <https://github.com/oloapinivad/AQUA/blob/main/diagnostics/global_ocean-diagnostic/notebooks/global_ocean.ipynb>`_
        
Detailed API
------------

This section provides a detailed reference for the Application Programming Interface (API) of the "global_ocean" diagnostic,
produced from the diagnostic function docstrings.

.. automodule:: global_ocean
    :members:
    :undoc-members:
    :show-inheritance:
