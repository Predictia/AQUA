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

Regrid and interpolation capabilities
-------------------------------------

AQUA provides functions to interpolate and regrid data to match the spatial resolution of different datasets. 
AQUA regridding functionalities are based on the external tool `smmregrid <https://github.com/jhardenberg/smmregrid>`_ which 
operates sparse matrix computation based on externally-computed weights.

Basic usage
^^^^^^^^^^^

When the ``Reader`` is called, if regrid functionalities are needed, the target grid has to be specified.

.. code-block:: python

    reader = Reader(model='IFS-NEMO', exp='historical-1990', source='hourly-native-atm2d',
                    regrid='r100')
    data = reader.retrieve()
    data_r = reader.regrid(data)

This will return an ``xarray.Dataset`` with the data lazily regridded to the target grid.
We can then use the ``data_r`` object for further processing and only the needed data
will be loaded in memory when necessary.

Concept
^^^^^^^

The idea of the regridder is first to generate the weights for the interpolation and
then to use them for each regridding operation. 
The reader generates the regridding weights automatically (with CDO) if not already
existent and stored in a directory specified in the ``config/machine/<machine-name>/catalog.yaml`` file.
A list of predefined target grids (only regular lon-lat for now) is available in the ``config/aqua-grids.yaml`` file.
For example, ``r100`` is a regular grid at 1° resolution.

.. note::
    If you're using AQUA on a shared machine, please check if the regridding weights
    are already available.

Vertical interpolation
^^^^^^^^^^^^^^^^^^^^^^

Aside from the horizontal interpolation, AQUA offers also the possibility to perform
a simple linear vertical interpolation building  on the capabilities of Xarray.
This is done with the ``vertinterp`` method of the ``Reader`` class.
This can of course be use in the combination of the ``regrid`` method so that it is possible to operate 
both interpolations in a few steps.
Users can also change the unit of the vertical coordinate.

.. code-block:: python

    reader = Reader(model="IFS", exp="tco2559-ng5", regrid = 'r100', source="ICMU_atm3d")
    data = reader.retrieve()
    field = reader.regrid(data['u'][0:5,:,:])
    interp = reader.vertinterp(field, [830, 835], units = 'hPa', method = 'linear')

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
