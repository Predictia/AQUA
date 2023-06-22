Dummy Diagnostic
================

Description
-----------

Dummy diagnostic provides an example on how diagnostics of the AQUA framework should be organised and written.
The dummy diagnostic follows a class structure and consists of the files:

* `dummy_class.py`: a python file in which the DummyDiagnostic class constructor and the other class methods are included;
* `dummy_func.py`: a python file which contains functions that are called and used in the dummy class;
* `env-dummy.yml`: a yml file with the required dependencies for the dummy diagnostic;
* `notebooks/dummy.ipynb`: an ipython notebook which uses the dymmy class and its methods;
* `README.md` : a reame file which contains some tecnical information on how to install the dummy diagnostic and its environment. 

This documentation provides also guidelines on how a diagnostic developer should write documentation about his/her diagnostic,
covering a short description of its contents and of its scientific basis. 
In case the diagnostic is bae on some already published material it is strongly 
recommended to include references to the inherent literature (we have a reference list below).
Please try to adhere to the following scheme as far as possible.

Input variables example:
------------------------

* `tprate` (total precipitation rate, GRIB paramid 260048)
* `2t`     (2 metre temperature, GRIB pramid 167)

Output 
------

List here types of files/datasets produced by the diagnostic

Methods used
------------

Examples from the DummyDiagnostic class:

* "DummyDiagnostic": the Dummy diagnostic class;
* "__init__": the Dummy diagnostic class;
* "_reader": method to initialise the Reader class;
* "retrieve": method to retrieve the data from the Reader class;

...


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

* `dummy.ipynb <https://github.com/oloapinivad/AQUA/blob/main/diagnostics/dummy-diagnostic/notebooks/dummy.ipynb>`_
        
Detailed API
------------

This section provides a detailed reference for the Application Programming Interface (API) of the "dummy" diagnostic,
produced from the diagnostic function docstrings.

.. automodule:: dummy
    :members:
    :undoc-members:
    :show-inheritance:
