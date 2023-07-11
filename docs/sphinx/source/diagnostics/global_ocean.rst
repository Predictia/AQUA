Global Ocean
================

Description
-----------

This package provides a set of diagnostics associated with the Global Ocean which in the current release include Hovmoller figures, time series analysis, and trends at different depths of the ocean.

All these diagnostics are produced in a consistent way, for a selected model simulation.

Structure
-----------

The global_ocean diagnostic follows a class structure and consists of the files:

* `global_ocean.py`: a python file which contains functions that are called and used in the global_ocean class;
* `notebooks/global_ocean.ipynb`: an ipython notebook which has the example of how to use the package;
* `README.md` : a readme file which contains some tecnical information on how to install the global_ocean diagnostic and its environment. 

Input variables example
------------------------

* `thetao` (total precipitation rate, GRIB paramid 150129)
* `so`     (2 metre temperature, GRIB pramid 151130)

Output 
------

This diagnostics exports all the data, which has been used to create the diagnostic figures.

  



Functions used 
---------------
Hovmoller_plot: This function requires data, a region, and the type of data processing. And it produces a Hovmoller plot of Temperature and salinity, including the processed data type. The region name supports all the major oceans and seas, in case users require a custom region, they can fill in the values of latitude, and longitude in the boxes.

.. code-block:: python

    hovmoller_plot(data, region= "Global Ocean",type = 'FullValue', latS, latN, lonE, lonW, output= True, output_dir= "output")

time_series: This function requires data, a region, and the type of data processing. And it produces a time series plot of Temperature and salinity, including the processed data type. The region name supports all the major oceans and seas, in case users require a custom region, they can fill in the values of latitude, and longitude in the boxes.

.. code-block:: python

    time_series(data,'Global Ocean', type="Anomaly",customise_level=False, levels=list,output = True,  output_dir="output")

multilevel_t_s_trend_plot: This function requires data, a region and optional depth level. And it produces a spatial trend plot of Temperature and salinity, The region name supports all the major oceans and seas, in case users require a custom region, they can fill in the values of latitude, and longitude in the boxes.

.. code-block:: python

    multilevel_t_s_trend_plot(data,'Atlantics Ocean', customise_level=False, levels=None,
                            output= True, output_dir = "output")

zonal_mean_trend_plot: This function requires data, a region. And it produces a zonal mean trend plot of Temperature and salinity. The region name supports all the major oceans and seas; in case users require a custom region, they can fill in the values of latitude and longitude in the boxes.

.. code-block:: python

   zonal_mean_trend_plot(data, region= "Indian Ocean ", output= True, output_dir="output")



References
----------



Example Plot(s)
---------------

.. figure:: figures/global_ocean1.png
    :width: 15cm

.. figure:: figures/global_ocean2.png
    :width: 15cm

.. figure:: figures/global_ocean3.png
    :width: 15cm

.. figure:: figures/global_ocean4.png
    :width: 15cm

Available demo notebooks
------------------------

Notebooks are stored in diagnostics/global_oceandiagnostic/notebooks

* `global_ocean.ipynb <https://github.com/oloapinivad/AQUA/blob/devel/ocean/diagnostics/global_ocean/notebooks/global_ocean.ipynb>`_
        
Detailed API
------------

This section provides a detailed reference for the Application Programming Interface (API) of the "global_ocean" diagnostic,
produced from the diagnostic function docstrings.

.. automodule:: global_ocean
    :members:
    :undoc-members:
    :show-inheritance:
