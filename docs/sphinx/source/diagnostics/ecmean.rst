ECmean4 Performance Indices
==========================

`ECmean4 <https://pypi.org/project/ECmean4>`_ is an open source package which has been integrated within AQUA. 
It integrates the capabilities of computing the Reichler and Kim Performance Indices (PIs), with some minor updates.

Description
===========

The ``performance_indices`` command is based on the ``performance_indices.py`` script which computes the `Reichler and Kim Performance Indices <https://journals.ametsoc.org/view/journals/bams/89/3/bams-89-3-303.xml>`_, usually known as PIs. 
Some minor differences from the original definition has been introduced, so that the PIs are computed on a common (user defined) grid rather than on the original grid.
From the original definition a few improvements has been introduced, producing the PIs also for a set of selected regions and seasons. 

PIs are the root mean square error of a 2D field normalized by the interannual variance estimated from the observations. Larger values implies worse performance of the climate models.

Structure
-----------

Please refer to the `official ECmean4 documentation <https://ecmean4.readthedocs.io/en/latest/>`_. 

Input variables 
---------------

For Performance Indices the followin variables are requested:

* `tprate` (total precipitation rate, GRIB paramid 260048)
* `2t`     (2 metre temperature, GRIB paramid 167)
* `msl`    (mean sea level pressure, GRIB paramid XXX)
* `t`
* `u`
* `v`
* `q`
* `sst`
* `so`
* `ci`

.. note ::
    Although PI can work directly on the model raw output, the interface file is made to work only with the Low Resolution Archive (LRA). 


Output 
------

The result is produced in a form a YAML file, indicating PIs for each variable, region and season, that can be stored for later evaluation. 
Most importantly, a figure is produced showing a score card for the different regions, variables and seasons.
For the sake of simplicity, the PIs figure is computed as the ratio between the model PI and the average value estimated over the (precomputed) ensemble of CMIP6 models. 

Methods and functions used
--------------------------

Please refer to the `official ECmean4 documentation <https://ecmean4.readthedocs.io/en/latest/>`_. 

Observations
------------

ECmean4 uses multiple sources for observations: please refer to the `Official Climatology description <https://ecmean4.readthedocs.io/en/latest/performanceindices.html#climatologies-available>`_

References
----------

* Reichler, T., and J. Kim, 2008: How Well Do Coupled Models Simulate Today's Climate?. Bull. Amer. Meteor. Soc., 89, 303-312, https://doi.org/10.1175/BAMS-89-3-303.

Example Plot(s)
---------------

.. figure:: figures/ecmean-pi.pdf
    :width: 10cm

    An example of the Performance Indices computed on tco2599-ng5 simulatation from NextGEMS Cycle2 run

Available demo notebooks
------------------------

Notebooks are stored in `diagnostics/ecmean/notebook`` (link to be corrected)

* `ecmean-test.ipynb <https://github.com/oloapinivad/AQUA/blob/main/diagnostics/dummy/notebooks/dummy_class_readerwrapper.ipynb>`_