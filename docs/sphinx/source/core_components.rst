Core Components
===============

Data Reading and Preprocessing
------------------------------

Supported File Formats
~~~~~~~~~~~~~~~~~~~~~~

AQUA supports a variety of climate data file formats, including:

- NetCDF
- GRIB
- HDF

Data Structures
~~~~~~~~~~~~~~~~

AQUA uses xarray data structures to manage and manipulate climate data. The primary data structures used in AQUA are:

- DataArray: Represents a single variable with multiple dimensions (e.g., time, latitude, longitude).
- Dataset: Represents a collection of DataArrays with shared dimensions.

Interpolation and Regridding
----------------------------

AQUA provides functions to interpolate and regrid data to match the spatial resolution of different datasets. The main functionalities include:

- Bilinear interpolation
- Nearest-neighbor interpolation
- Conservative regridding
- Advanced regridding methods (e.g., ESMF)

Averaging and Aggregation
-------------------------

AQUA offers various tools for averaging and aggregating climate data along spatial and temporal dimensions. Some of the key functions are:

- Spatial averaging: Calculates the average of a variable over a specified region.
- Temporal averaging: Calculates the average of a variable over a specified time period.
- Zonal averaging: Calculates the average of a variable along a specified latitude or longitude range.

Parallel Processing
--------------------

AQUA supports parallel processing to speed up the execution of diagnostics. This is achieved using the following approaches:

- Multithreading: Running multiple threads within a single process.
- Multiprocessing: Running multiple processes, each with its own Python interpreter.
- Distributed computing: Running computations across multiple nodes in a cluster, using tools like Dask.

To enable parallel processing, AQUA provides functions to manage and distribute tasks, allowing users to focus on writing their diagnostics without worrying about the underlying parallelization details.
