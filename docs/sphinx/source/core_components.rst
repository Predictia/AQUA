Core Components
===============

The `Reader` Class
------------------

AQUA access to data is provided by the `Reader` class, developed with the purpose to offer a centralized common data access point.
AQUA `Reader` can in fact access different file formats and data, from the FDB or from intake catalogues (NextGEMS), and delivers xarray objects.
On top of data access, the `Reader` is able to perform multiple operations on the data: interpolation and regridding, spatial and temporal averaging, metadata correction and streaming emulation. 

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

Basic Example
~~~~~~~~~~~~~~~~
Accessing data with the AQUA `Reader` is very straightforward.
In order to check what is available in the catalogue we can use the ``catalogue()`` function.
It returns the catalogue itself by default, that's why we use it with a semicolon at the end.
The data are classified in "models" (e.g. ICON, IFS etc.). Each model has a different "experiment" and there are different "sources" for each of experiment.

Let's try to load some ICON data as an example.
We first instantiate a Reader object specifying the type of data which we want to read from the catalogue.
The `Reader` access is build on a 3-level hierarchy, made of model, experiment and source. 

``reader = Reader(model="ICON", exp="ngc2009", source="atm_2d_ml_R02B09")``

Now we can read the actual data with the retrieve method.

``data = reader.retrieve(fix=False)``

The reader returns an xarray.Dataset with raw ICON data on the original grid

Interpolation and Regridding
----------------------------

AQUA provides functions to interpolate and regrid data to match the spatial resolution of different datasets. 
AQUA functionalities are based on the external tool  `smmregrid <https://intake.readthedocs.io/en/stable/>`_  which operates sparse matrix computation based on externally-computed weights. 
For this reason, AQUA interpolation has been developed on CDO, and allows for interpolation of multiple grids (unstructured, curvilinear, healpix, etc.) making use of multiple
interpolation methods (nearest-neighbor, conservative, bilinear, etc.). 

The idea of the regridder is to generate first the weights for the interpolation and then to use them for each regridding operation.
In other words, weights are computed externally by CDO (an operation which needs to be done only once) and then stored on the machine so that further operations are considerably fast. 
Such approach has two main advantages:

1. All operations are done in memory, so that no I/O is required and the operations is faster than CDO
2. Operations can easily parallelized with Dask, bringing further speedup. 

In the long term, it will be possible to support also other interpolation software, as ESMF or MIR. 


Averaging and Aggregation
-------------------------

Since AQUA is based on xarray, all the spatial and temporal aggregation options are available by the default. 
On top of that, AQUA provides the area of each dataset to be loaded so area-weighted averages can be produced without hassle. 
When we instantiate the reader object, grid areas for the source files are computed if not already available. 
After this we can use them to do spatial averaging using the `fldmean` method, obtaining timeseries of global (field) averages.
For example, we the following commands:

``tprate = data.tprate
global_mean = reader.fldmean(tprate)``

we get a timeseries of the global average tprate.


Fixing: Metadata correction 
---------------------------

Streaming simulation
--------------------

Parallel Processing
-------------------

AQUA supports parallel processing to speed up the execution of diagnostics. This is achieved using distributed computing provided by dask.
