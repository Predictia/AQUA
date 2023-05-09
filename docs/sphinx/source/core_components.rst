Core Components
===============

The `Reader` Class
------------------

AQUA access to data is provide by a class defined as `Reader`, which performs multiple operations on the data and delivers xarray objects.
The `Reader` can access data from FDB or from intake catalogs, which can be made of multiple file formats. 

The `Reader` class is shipped with multiple methods that support interpolation and regridding, spatial and temporal averaging and other pre-processing functionalities.

Data Reading and Preprocessing
------------------------------

Supported File Formats
~~~~~~~~~~~~~~~~~~~~~~

AQUA supports a variety of climate data file formats, including:

- NetCDF
- GRIB
- FDB
- Zarr

Data Structures
~~~~~~~~~~~~~~~~

AQUA uses xarray data structures to manage and manipulate climate data. The primary data structures used in AQUA are:

- DataArray: Represents a single variable with multiple dimensions (e.g., time, latitude, longitude).
- Dataset: Represents a collection of DataArrays with shared dimensions.

Interpolation and Regridding
----------------------------

AQUA provides functions to interpolate and regrid data to match the spatial resolution of different datasets. 
AQUA functionalities are based on the external tool  `smmregrid <https://intake.readthedocs.io/en/stable/>`_  which operates sparse matrix computation based on externally-computed weights. 
For this reason, AQUA interpolation has been developed on CDO, and allow for interpolation of multiple grids (unstructured, curvilinear, healpix, etc.) making use of multiple
interpolation methods (nearest-neighbor, conservative, bilinear, etc.). 
Weights are computed externally by CDO and then stored on the machine so that further operations are considerably fast. Such approach has two main advantages:

1. All operations are done in memory, so that no I/O is required and the operations is faster than CDO
2. Operations can easily parallelized with Dask, bringing further speedup. 

In the long term, it will be possible to support also other interpolation software, as ESMF or MIR. 

Averaging and Aggregation
-------------------------

Since AQUA is based on xarray, all the spatial and temporal aggregation options are available by the default. 
On top of that, AQUA provides the area of each dataset to be loaded so area-weighted averages can be produced without hassle. 

Parallel Processing
--------------------

AQUA supports parallel processing to speed up the execution of diagnostics. This is achieved using distributed computing provided by dask.
