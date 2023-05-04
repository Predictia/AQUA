Getting Started
===============

Basic Concepts
--------------

AQUA is designed to simplify the process of running diagnostics on high-resolution climate models. 
The package is built around a few core concepts:

- Data reading and preprocessing: Data exposed through `intake` catalogs, and represented as `xaray` objects. This allows to easily read and preprocess data from a variety of sources, including local files, remote servers, and cloud storage.
- Data fixing: AQUA provides capabilities to change metadata (e.g. variable names) and data themselves (e.g. convert to different units).
- Interpolation and regridding: AQUA offers robust interpolation and regridding functionality to align datasets with different grids and spatial resolutions.
- Averaging and aggregation: AQUA provides tools to perform temporal and spatial averaging and aggregation of climate data.
- Diagnostics: AQUA includes a set of built-in diagnostic tools, and it allows users to create custom diagnostics as well.
- Parallel processing: AQUA supports parallel processing through `dask` to speed up the execution of diagnostics.

Workflow Overview
-----------------

The typical workflow when using AQUA consists of the following steps:

1. Data preparation: Read and preprocess the input data (e.g., climate model outputs, observations) using AQUA's data handling functions.
2. Averaging and aggregation: Perform necessary temporal and spatial averaging or aggregation using AQUA's built-in tools if needed.
3. Interpolation and regridding: Align datasets with different spatial resolutions using AQUA's interpolation and regridding tools.

Example Use Case
----------------

To demonstrate a simple use case, we will walk you through an example of using AQUA to interpolate atmospheric
temperature data to 1°x1° grid and calculate compute time series of mean global temperature on original grid.

.. code-block:: python

   from aqua import Reader

   # Instantiate a Reader object specifying the type of data which we want to read from the catalogue. 
   # We also specify that we would like to regrid to a 1°x1° grid.
   reader = Reader(model="ICON", exp="ngc2009", source="atm_2d_ml_R02B09", regrid='r100')

   # Retrieve the data. The fix=True will convert variable names to GRIB standard. 
   data = reader.retrieve(fix=True)

   # Perform temperal averaging of the first 10 time steps, using standard xarray syntax.:
   tasr_mean = data['2t'][:10].mean(dim='time')
   
   # Regrid the data to a 1°x1° grid
   tasr_mean_regrided = reader.regrid(tasr_mean)

   # Do weighted average of the data on original grid:
   global_mean = reader.fldmean(data['2t'][100:200, :])


For more detailed examples and tutorials, refer to the Examples and Tutorials section of this documentation
or explore the Jupyter notebooks provided with AQUA.
