Ocean Circulation
================

Description
-----------

ocean_circulation provides an example on how diagnostics of the AQUA framework should be organised and written.
This documentation provides also guidelines on how a diagnostic developer should write documentation about their diagnostic,
covering a short description of its contents and of its scientific basis. The documentation should explain in a clear and concise manner
what the diagnostic is about and what it is supposed to be doing  and the motivation behind it (i.e. which phenomenon or physical process 
is diagnosed and why it is important in the context of the analysis of high-resulution climate simulations).
In case the diagnostic is based on some already published material it is strongly 
recommended to include references to the inherent literature (we have a reference list below).
Please try to adhere to the suggested scheme as far as possible.

Structure
-----------

The ocean_circulation diagnostic follows a class structure and consists of the files:

* `ocean_circulation_class.py`: a python file in which the ocean_circulationDiagnostic class constructor and the other class methods are included;
* `ocean_circulation_func.py`: a python file which contains functions that are called and used in the ocean_circulation class;
* `env-ocean_circulation.yml`: a yaml file with the required dependencies for the ocean_circulation diagnostic;
* `notebooks/ocean_circulation.ipynb`: an ipython notebook which uses the dymmy class and its methods;
* `README.md` : a readme file which contains some tecnical information on how to install the ocean_circulation diagnostic and its environment. 

Input variables example
------------------------

* `ocpt` (Ocean potential temperature, GRIB paramid 150129)
* `so`     (Sea water practical salinity, GRIB pramid 151130)

Output 
------

List here types of files/datasets produced by the diagnostic

Methods used
------------

Examples from the ocean_circulationDiagnostic class contained in the ocean_circulation_class.py file:

* "ocean_circulationDiagnostic": the ocean_circulation diagnostic class;
* "retrieve": method to retrieve the data from the Reader class;
* "fldmean": method to compute the field mean of the retrieved data;
* "multiplication": method to compute the multiplication of the retrieved data. 
                    It is an example of method that uses of external functions of the module ocean_circulation_func

...

Functions used
--------------

fn.plot_stratification(data, region= False,time = "JJA",latS, latN, lonW, lonE, output= True, output_dir="./output")
fn.plot_spatial_mld(dmod, region= "gulf_of_mexico",time = "JJA", output= True, output_dir="./output")

Observations
------------

EN4 Observation datasets user in this diagnostics.

References
----------

.. * E. Empty, D. ocean_circulation et al. (2023) The art of saying nothing. Emptyness, 1: 0-1. `DOI <http://doi.org/00.0000/e-00000-000.xxxx>`_


Example Plot(s)
---------------

.. figure:: figures/ocean_circulation1.png
    :width: 10cm

    This is stratification plot. 

.. figure:: figures/ocean_circulation2.png
    :width: 10cm

    This mixed layer depth plot

Available demo notebooks
------------------------

Notebooks are stored in diagnostics/ocean_circulation-diagnostic/notebooks

* `ocean_circulation.ipynb <https://github.com/oloapinivad/AQUA/blob/devel/ocean_circulation/diagnostics/ocean_circulation/notebooks/ocean_circulation.ipynb>`_
        
Detailed API
------------

This section provides a detailed reference for the Application Programming Interface (API) of the "ocean_circulation" diagnostic,
produced from the diagnostic function docstrings.

.. automodule:: ocean_circulation
    :members:
    :undoc-members:
    :show-inheritance:
