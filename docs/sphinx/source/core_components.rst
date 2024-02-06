Core Components
===============

Here we describe the core components of the AQUA library.
Specifically with core components we refer to the code contained in the folder ``aqua``.
These are tools that are used to read, process and visualize data, not specific of a single diagnostic.
Some extra functionalities can be found in the :ref:`advanced-topics` section.

The Reader class
----------------

The ``Reader`` class provides AQUA access to data, developed to offer a centralized common data access point.
AQUA ``Reader`` can, in fact, access different file formats and data from the FDB or intake catalogues, 
and delivers xarray objects.
On top of data access, the ``Reader`` is also able to perform multiple operations on the data:
interpolation and regridding, spatial and temporal averaging and metadata correction. 
These are described in the following sections.
The ``Reader`` class is also able to perform parallel processing and to stream data,
since high-resolution data can be too large to be loaded in memory all at once
and it may be necessary to process data in chunks or even step by step.

Input and Output formats
^^^^^^^^^^^^^^^^^^^^^^^^

AQUA supports a variety of climate data file input formats:

- **NetCDF**
- **GRIB** files
- **Zarr**
- **FDB** GRIB

After the data are retrieved, the ``Reader`` class returns an xarray object,
specifically an ``xarray.Dataset``, where only the metadata are loaded in memory.

.. note::
    Since metadata are the minimum information needed to load the data and prepare the processing,
    large sets of numerous NetCDF files are easy to read, but they may require
    to open a large amount of data to be able to check all the metadata.
    We then suggest, if low performance is experienced, to use the Zarr format
    on top of the NetCDF format, to significantly improve the performance of the data access.

Catalogue Exploration
^^^^^^^^^^^^^^^^^^^^^

To check what is available in the catalogue, we can use the ``inspect_catalogue()`` function.
Three hierarchical layer structures describe each dataset.
At the top level, there are *models* (keyword ``model``) (e.g., ICON, IFS-NEMO, IFS-FESOM, etc.). 
Each model has different *experiments* (keyword ``exp``) and each experiment can have different *sources* (keyword ``source``).

Calling, for example:

.. code-block:: python

    from aqua import inspect_catalogue
    inspect_catalogue(model='CERES')

will return experiments available in the catalogue for model CERES.

.. warning::
    The ``inspect_catalogue()`` and the ``Reader`` are based on the machine and AQUA path configuration.
    If you don't find a source you're expecting, please check these are correctly set (see :ref:`getting_started`).

Reader basic usage
^^^^^^^^^^^^^^^^^^

Once you know which dataset you want to access, a call to the ``Reader`` can be done.
The basic call to the ``Reader`` is:

.. code-block:: python

    from aqua import Reader
    reader = Reader(model='IFS-NEMO', exp='historical-1990', source='lra-r100-monthly')
    data = reader.retrieve()

This will return a ``Reader`` object that can be used to access the data.
The ``retrieve()`` method will return an ``xarray.Dataset`` to be used for further processing.

.. note::
    The basic call enables fixer, area and time average functionalities, but no regridding.

If some information about the data is needed, it is possible to use the ``info`` method of the ``Reader`` class.

.. code-block:: python

    reader.info()

Dask and Iterator access
^^^^^^^^^^^^^^^^^^^^^^^^

The standard usage of the ``Reader`` class will load metadata in memory and
make the data available for processing.
This is the standard behaviour of the ``Reader`` class, where ``xarray`` and ``dask``
capabilities are used to retrieve the data.

However, the ``Reader`` class is also able to allow a streaming of data, 
where the data are loaded in chunks and processed step by step.

Please check the :ref:`iterators` section for more details.

.. note::
    Dask access to data is available also for FDB data.
    Since a specific intake driver has been developed, if you're adding FDB sources,
    we suggest to read the :ref:`FDB_dask` section.

Regridding capabilities
-----------------------

Fixer functionalities
---------------------

Metadata Correction
^^^^^^^^^^^^^^^^^^^^

Data Model and Coordinate Correction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Time Aggrigation
----------------

Spatial Averaging
-----------------

Streaming of data
-----------------

.. _accessors:
Accessors
---------

Parallel Processing
-------------------

Graphic tools
-------------
