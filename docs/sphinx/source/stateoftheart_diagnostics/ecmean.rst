ECmean4 Performance Metrics
===========================

`ECmean4 <https://pypi.org/project/ECmean4>`_ is an open source package which has been integrated within AQUA,
aiming at computing basic performance metrics. It specifically covers the Reichler and Kim Performance Indices (PIs)
and the so-called Global Mean (GMs), i.e. global averages for several fields compared againt observations.

Together, those numbers provides an estimates of the climate models climatological *skill* of some selected atmospheric and oceanic fields.

Description
-----------

The diagnostic computes two metrics. On the one hand, the `Reichler and Kim Performance Indices <https://journals.ametsoc.org/view/journals/bams/89/3/bams-89-3-303.xml>`_, usually known as PIs. 
are computed following the ECmean4 implementation: some minor differences from the original definition has been introduced,
so that the PIs are computed on a common (1x1 deg) grid rather than on the model grid.
From the original definition a few improvements has been introduced, using updated climatologies and provides the PIs also for a set of selected regions and seasons. 

From the formal point of view, PIs are computed as the root mean square error of a selected 2D field normalized by the
interannual variance estimated from the observations. Larger values implies worse performance (i.e. larger bias).
In the plots produced by ECmean4 implementation, PIs are normalized by the (precomputed) average of CMIP6 climate models,
so that number smaller than one implies a better performance than CMIP6 model.

On the other hand, the Global Mean (GMs) metric is computed. These are simply the average of many dynamical and physical fields which are 
compared against a set of pre-computed climatological values for both the atmosphere and the ocean (e.g. land temperature, salinity, etc.). 
Different observational datasets are taken in consideration for each variable, providing an estimate of the plausible variability in the form of interannual standard deviation.
GMs provides also estimate for the radiative budget  and for the hydrological cycle (including integrals over land and ocean) 
and other quantities useful for fast model assessment and for model tuning.

Structure
-----------

For detailed information on the code, please refer to the `official ECmean4 documentation <https://ecmean4.readthedocs.io/en/latest/>`_.  

Input variables 
---------------

For **Performance Indices** the following variables are requested:

* ``mtpr`` (Mean total precipitation rate, GRIB paramid 235055)
* ``2t``     (2 metre temperature, GRIB paramid 167)
* ``msl``    (mean sea level pressure, GRIB paramid 151)
* ``metss``  (eastward wind stress, GRIB paramid 180)
* ``mntss``  (northward wind stress, GRIB paramid 181)
* ``t``      (air temperature, GRIB paramid 130)        
* ``u``      (zonal wind, GRIB paramid 131)
* ``v``      (meridional wind, GRIB paramid 132)
* ``q``      (specific humidity, GRIB paramid 133)
* ``avg_tos``    (sea surface temperature, GRIB paramid 263101)
* ``avg_sos``    (sea surface salinity, GRIB paramid 263100)
* ``avg_siconc``     (sea ice concentration, GRIB paramid 263001)
* ``msshf``     (surface sensible heat flux, GRIB paramid 235033, required for net surface flux computation)
* ``mslhf```    (surface latent heat flux, GRIB paramid 235034, required for net surface flux computation)
* ``msnlwrf``  (surface net longwave radiation flux, GRIB paramid 235038, required for net surface flux computation)
* ``msnswrf``   (surface net shortwave radiation flux, GRIB paramid 235037, required for net surface flux computation)
* ``msr``      (snowfall rate, GRIB paramid 235031, required for net surface flux computation)

3D fields are zonally averaged, so that the PIs reports the performance on the zonal field. 

For **Global Means**, the following variables are requested

* ``mtpr`` (Mean total precipitation rate, GRIB paramid 235055)
* ``mer`` (Mean evaporation rate, GRIB paramid 235043)
* ``2t``     (2 metre temperature, GRIB paramid 167)
* ``msl``    (mean sea level pressure, GRIB paramid 151)
* ``metss``  (eastward wind stress, GRIB paramid 180)
* ``mntss``  (northward wind stress, GRIB paramid 181)
* ``t``      (air temperature, GRIB paramid 130)        
* ``u``      (zonal wind, GRIB paramid 131)
* ``v``      (meridional wind, GRIB paramid 132)
* ``q``      (specific humidity, GRIB paramid 133)
* ``tcc``    (total cloud cover, GRIB paramid 228164)
* ``mtnswrf``  (top net shortwave radiation, GRIB paramid 235039)
* ``mtnlwrf``  (top net longwave radiation, GRIB paramid 235040)
* ``avg_tos``    (sea surface temperature, GRIB paramid 263101)
* ``avg_sos``    (sea surface salinity, GRIB paramid 263100)
* ``avg_siconc``     (sea ice concentration, GRIB paramid 263001)
* ``msshf``     (surface sensible heat flux, GRIB paramid 235033, required for net surface flux computation)
* ``mslhf```    (surface latent heat flux, GRIB paramid 235034, required for net surface flux computation)
* ``msnlwrf``  (surface net longwave radiation flux, GRIB paramid 235038, required for net surface flux computation)
* ``msnswrf``   (surface net shortwave radiation flux, GRIB paramid 235037, required for net surface flux computation)
* ``msr``      (snowfall rate, GRIB paramid 235031, required for net surface flux computation)


For both diagnostics, if a variable (or more) is missing, blank line will be reported in the output figures. 

.. note ::
    ECmean4 is made to work with CMOR variables, but can handle name and file conversion with specification of
    an `interface file <https://ecmean4.readthedocs.io/en/latest/configuration.html#interface-files>`_.
    An AQUA specific one has been designed for this purpose to work with Climate DT Phase 1. 
    Updates in the Data Governance will require updates to the interface file.  
    In addition, although PI and GM can work directly on the model raw output, the interface file is made to work only
    with the Low Resolution Archive (LRA) to reduce the amount of computation required. 


Output 
------

The result are stored as a YAML file, indicating PIs and GMs for each variable, region and season, that can be stored for later evaluation.
Most importantly, a figure for GMs and a figure for PIs are produced showing a score card for the different regions, variables and seasons.
For the sake of simplicity, the PIs figure is computed as the ratio between the model PI and the average value estimated over the (precomputed) ensemble of CMIP6 models. 
Numbers lower than one implies that the model is performing better than the average of CMIP6 models. 

Similarly, the GMs are reported as a score card with the average of the field, together with observational value reported in a 
smaller font, and colorscale which tells how many standard deviations from the interannual variability the model is far from observation. 
The whiter the color, the more reliable is the model output.

Methods and functions used
--------------------------

Please refer to the `official ECmean4 documentation <https://ecmean4.readthedocs.io/en/latest/>`_. 

Observations
------------

ECmean4 uses multiple sources as reference climatologies: please refer to the climatology description for `Performance Indices <https://ecmean4.readthedocs.io/en/latest/performanceindices.html#climatologies-available>`_ 
and for `Global Mean <https://ecmean4.readthedocs.io/en/latest/globalmean.html#climatology-computation>`_ to get more insight. 

References
----------

* Reichler, T., and J. Kim, 2008: How Well Do Coupled Models Simulate Today's Climate?. Bull. Amer. Meteor. Soc., 89, 303-312, https://doi.org/10.1175/BAMS-89-3-303.

Example Plot(s)
---------------

.. figure:: figures/ecmean-pi.png
    :width: 15cm

    An example of the Performance Indices computed on a single year of the tco2599-ng5 simulation from NextGEMS Cycle2 run.

.. figure:: figures/ecmean-gm.png
    :width: 15cm

    An example of the Global Mean computed on 30 years of the tco2599-ng5 simulation from NextGEMS Cycle4 run.

Available demo notebooks
------------------------

Notebooks are stored in ``notebooks/diagnostics/ecmean``.

* `ecmean-destine.ipynb <https://github.com/DestinE-Climate-DT/AQUA/blob/main/notebooks/diagnostics/ecmean/ecmean-destine.ipynb>`_
