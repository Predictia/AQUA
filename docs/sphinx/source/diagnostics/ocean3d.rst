Ocean3D
=======

Description
-----------

This package contains two submodules to monitor and evaluate the 3D ocean evolution and mean state:

- ``Ocean Drifts``: to characterize and monitor model drifts.
- ``Ocean Circulation``: to evaluate the realism of the model in simulating key precursors of the ocean circulation.

All these diagnostics are produced in a consistent way for a selected model simulation.
Additionally, there are newly added multi-model diagnostics functions under ocean drift and circulation.


Structure
---------

The ocean3d diagnostic follows a class structure and consists of the following files:

- ``cli``: Folder to run the ocean diagnostics from the command line;
  - ``cli_ocean3d.py``: a python file that contains the command line ocean diagnostics;
  - ``config.yaml``: config file containing details for the cli;

- ``config``: Folder containing necessary information for ocean3d;
  - ``regions.yaml``: yaml file containing the predefined regions where users can also define regions;

- ``notebooks``: Folder contains notebooks demonstrating the functions;
  - ``ocean_drifts.ipynb``: an ipython notebook with examples on how to apply the ocean drift diagnostics;
  - ``ocean_circulation.ipynb``: an ipython notebook with examples on how to apply the ocean circulation diagnostics;
  - ``multi_model_analysis.ipynb``: an ipython notebook with examples on how to apply the multi model diagnostics;

- ``ocean3d``: Folder containing the ocean3d functions;
  - ``ocean_circulation``: Folder containing the ocean circulation functions;
    - ``multi_model``: Folder containing the ocean circulation functions;
    - ``mld.py``: a python file that contains the functions for mixed layer depth;
    - ``stratification.py``: a python file that contains the functions for stratification;
  - ``ocean_drifts``: Folder containing the ocean drift functions;
    - ``multi_model``: Folder containing the ocean drift functions;
    - ``hovmoller_plot.py``: a python file that contains the functions for hovmoller plot;
    - ``time_series.py``: a python file that contains the functions for time series;
    - ``trends.py``: a python file that contains the functions for trends;
  - ``ocean_utils.py``: a python file that contains functions used in both ocean3d diagnostic modules;

- ``README.md``: a readme file that contains some technical information on how to install the ocean3d diagnostic and its environment. 

Input variables example
------------------------

* ``avg_thetao`` (Ocean potential temperature, GRIB paramid 150129)
* ``avg_so``     (Sea water practical salinity, GRIB paramid 151130)



Output 
------

This module exports all the data and diagnostics  used to create the different figures except the multi-model diagnostics.
  

prepare the o3d request
---------------------------
ocean3d request looks like this but, some details change with functions. To look into a more detailed request. Also, the request for multi-model analysis looks different.  we recommend to look into the notebooks to get clear idea. 

.. code-block:: python

    o3d_request= {'model':'IFS-NEMO', 'exp':'historical-1990', 'source': 'lra-r100-monthly', 'data': data,
                  'obs_data': obs_data, 'region':'Labrador Sea', 'latS':None, 'latN':None, 'lonW':None, 'lonE':None,
                  'output':True, "time" : "February", 'output_dir':'./output'}


Functions used 
---------------

.. code-block:: python

    hovmoller_plot(o3d_request)

*hovmoller_lev_time_plot*: This function requires data, a region. 
It produces a Hovmöller plot of regionally averaged temperature and salinity including three types of subplots. 
The region name supports all the major oceans and seas, in case users require a custom region,
they can fill in the values of latitude, and longitude in the boxes as desired.


.. code-block:: python

    time_series(o3d_request)

*time_series*: This function requires data, a region. 
It produces time series plots of regionally averaged temperature and salinity including three types of subplots
for a predefined or customized list of vertical levels. 
The region name supports all the major oceans and seas, in case users require a custom region,
they can fill in the values of latitude, and longitude in the boxes.


.. code-block:: python

    multilevel_trend(o3d_request)


*multilevel_trend*: This function requires data, a region, and optional depth levels. 
It produces lon-lat maps of linear temporal trends of temperature and salinity over the selected
region for a predefined or customized list of vertical levels. 
The region name supports all the major oceans and seas, in case users require a custom region,
they can fill in the values of latitude, and longitude in the boxes.


.. code-block:: python

   zonal_mean_trend_plot(o3d_request)

*Zonal Mean Trend Plot*: This function requires data for a region. 
It produces plots of zonally averaged linear temporal trends plot of temperature and salinity as a function of depth and latitude. 
The zonal average is produced over the selected region, whose name supports all the major oceans and seas;
in case users require a custom region, they can fill in the values of latitude and longitude in the boxes.


.. code-block:: python

    stratification(o3d_request)

*Stratification plot*: This function requires data, a region, and the time of the climatology. 
It produces a stratification plot of Temperature, salinity and Density, including the overlapped data with the observation. 
The region name supports all the major oceans and seas, in case users require a custom region, they can fill in the values of latitude,
and longitude in the boxes.


.. code-block:: python

    plot_spatial_mld_clim(o3d_request)

Mixed Layer Depth Plot: This function requires data, a region, and the time of the climatology. 
It produces a time series plot of temperature and salinity.
Users have the option of choosing whether they want to use the whole obs data or overlapped obs data with the model. 
The region name supports all the major oceans and seas; in case users require a custom region, they can fill in the values of latitude,
and longitude in the boxes.


Methods used 
---------------
All regional averages have been produced with area weights.

Temporal trends are computed as linear trends and estimated over the whole temporal span of the dataset.

The mixed layer depth is computed by the function ``compute_mld_cont`` from sigma0 monthly fields following the criteria from de Boyer Montegut et al (2004)

Density fields are computed from absolute salinity and conservative temperature fields using the TEOS-10 equations.
Absolute salinity and conservative temperature are also computed from practical salinity and potential temperature fields with
TEOS-10 equations.


Observations  
---------------

EN4.2.2.g10 ocpt and so observations for the period 1950-2022


.. This set of diagnostics has been developed to monitor potential drifts and initialization shock in the models.
.. Observations do not provide any added value for the identification of the drift and were not considered.


References
----------
de Boyer Montégut, C., Madec, G., Fischer, A. S., Lazar, A., and Iudicone, D. (2004): Mixed layer depth over the global ocean: An examination of profile data and a profile-based climatology. J. Geophys. Res., 109, C12003, doi:10.1029/2004JC002378

Gouretski and Reseghetti (2010): On depth and temperature biases in bathythermograph data: development of a new correction scheme based on analysis of a global ocean database. Deep-Sea Research I, 57, 6. doi: http://dx.doi.org/10.1016/j.dsr.2010.03.011

https://www.teos-10.org/


A code to compute very efficiently the linear trends has been adapted from this website:
https://stackoverflow.com/questions/52108417/how-to-apply-linear-regression-to-every-pixel-in-a-large-multi-dimensional-array


Example Plot(s)
---------------


* This is an example of the multipanel plots of the spatially averaged T, S timeseries at different levels

.. figure:: figures/IFS-NEMO-historical-1990-lra-r100-monthly_time_series_atlantic_ocean-1.jpg
    :width: 18cm


* This is an example of the multi-panel plots of lat-lon  maps of temporal trends in T, S at different levels

.. figure:: figures/IFS-NEMO-historical-1990-lra-r100-monthly_multilevel_t_s_trend_atlantic_ocean-1.jpg
    :width: 18cm


* This is an example of the plots of lat-depth maps of temporal trends in T, S

.. figure:: figures/ocean3d4.png
    :width: 18cm


* This is an example of one of the climatological stratification profiles.

.. figure:: figures/IFS-NEMO-historical-1990-lra-r100-monthly_stratification_Feb_clim_labrador_sea-1.jpg
    :width: 20cm


* This is an example of one of the mixed-layer depth climatologies. Unit is meter. 

.. figure:: figures/IFS-NEMO-historical-1990-lra-r100-monthly_spatial_MLD_Jun-Jul-Aug_weddell_sea-1.jpg
    :width: 20cm


Available demo notebooks
------------------------

Notebooks are stored in diagnostics/ocean3d/notebooks

* `global_ocean.ipynb <https://github.com/oloapinivad/AQUA/blob/main/diagnostics/ocean3d/notebooks/ocean_drifts.ipynb>`_

    
* `ocean_circulation.ipynb <https://github.com/oloapinivad/AQUA/blob/main/diagnostics/ocean3d/notebooks/ocean_circulation.ipynb>`_


* `multi_model_analysis.ipynb <https://github.com/oloapinivad/AQUA/blob/main/diagnostics/ocean3d/notebooks/multi_model_analysis.ipynb>`_
    
Detailed API
------------

This section provides a detailed reference for the Application Programming Interface (API) of the "ocean3d" diagnostic,
produced from the diagnostic function docstrings.

.. automodule:: ocean3d
    :members:
    :undoc-members:
    :show-inheritance:
