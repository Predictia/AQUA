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
    The basic call enables fixer, area and time average functionalities, but no regridding or streaming.

If some information about the data is needed, it is possible to use the ``info()`` method of the ``Reader`` class.

.. warning::
    Every ``Reader`` instance brings information about the grids and fixes of the retrieved data.
    If you're retrieving data from many sources, please instantiate a new ``Reader`` for each source.

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

When the ``Reader`` is called, if regrid functionalities are needed, the target grid has to be specified
during the class initialization:

.. code-block:: python

    reader = Reader(model='IFS-NEMO', exp='historical-1990', source='hourly-native-atm2d',
                    regrid='r100')
    data = reader.retrieve()
    data_r = reader.regrid(data)

This will return an ``xarray.Dataset`` with the data lazily regridded to the target grid.
We can then use the ``data_r`` object for further processing and the data
will be loaded in memory only when necessary, allowing for further subsetting and processing.

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

In other words, weights are computed externally by CDO (an operation that needs to be done only once) and 
then stored on the machine so that further operations are considerably fast. 

Such an approach has two main advantages:

1. All operations are done in memory so that no I/O is required, and the operations are faster than with CDO
2. Operations can be easily parallelized with Dask, bringing further speedup.

.. note::
    In the long term, it will be possible to support also other interpolation software,
    such as `ESMF <https://earthsystemmodeling.org/>`_ or `MIR <https://github.com/ecmwf/mir>`_.

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

.. _fixer:
Fixer functionalities
---------------------

The need of comparing different datasets or observations is very common when evaluating climate models.
However, datasets may have different conventions, units, and even different names for the same variable.
AQUA provides a fixer tool to standardize the data and make them comparable.

The general idea is to convert data from different models to a uniform file format
with the same variable names and units. The default format is **GRIB2**.

The fixing is done by default when we initialize the ``Reader`` class, 
using the instructions in the ``config/fixes`` folder.

The ``config/fixes`` folder contains fixes in YAML files.
A new fix can be added to the folder and the filename can be freely chosen.
By default, fixes files with the name of the model or the name of the DestinE project are provided.

Fixes can be specified in two different ways:

- Using the ``fixer_name`` definitions, to be then provided as a metadata in the catalog.
  This represents fixes that have a common nickname which can be used in multiple sources when defining the catalog.
  There is the possibility of specifing a `parent` fix so that a fix can be re-used with minor correction, merging small change to a larger family.
- Using the source-based definition.
  Each source can have its own specific fix, or alternatively a ``default.yaml`` that can be used in the case of necessity.
  Please note that this is the older AQUA implementation and will be deprecated in favour of the new `family` approach.

.. note::
    A ``default.yaml`` is used for common unit corrections if no specific fix is provided.
    If no ``fixer_name`` is provided and ``fix`` is set to ``True``, the code will look for a
    ``fixer_name`` called ``<MODEL_NAME>-default``.

Concept
^^^^^^^

The fixer performs a range of operations on data:

- adopts a common **coordinate data model** (default is the CDS data model): names of coordinates and dimensions (lon, lat, etc.),
  coordinate units and direction, name (and meaning) of the time dimension. (See :ref:`coord-fix` for more details)
- changes variables name deriving the correct metadata from GRIB tables.
  The fixer can identify these derived variables by their ShortNames and ParamID (ECMWF and WMO eccodes tables are used).
- derives new variables executing trivial operations as multiplication, addition, etc. (See :ref:`metadata-fix` for more details)
  In particular, it derives from accumulated variables like ``tp`` (in mm), the equivalent mean-rate variables
  (like ``mtpr``). (See :ref:`metadata-fix` for more details)
- using the ``metpy.units`` module, it is capable of guessing some basic conversions.
  In particular, if a density is missing, it will assume that it is the density of water and will take it into account.
  If there is an extra time unit, it will assume that division by the timestep is needed. 


.. _metadata-fix:
Metadata Correction
^^^^^^^^^^^^^^^^^^^^

.. _coord-fix:
Data Model and Coordinates Correction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Time Aggregation
----------------

Input data may not be available at the desired time frequency. It is possible to perform time averaging at a given
frequency by using the ``timmean`` method. 

.. code-block:: python

    reader = Reader(model="IFS", exp="tco2559-ng5", source="ICMGG_atm2d")
    data = reader.retrieve()
    daily = reader.timmean(data, freq='daily')

Data have now been averaged at the desired daily timescale.
If you want to avoid to have incomplete average over your time period (for example, be sure that all the months are complete before doing the time mean)
it is possible to activate the ``exclude_incomplete=True`` flag which will remove averaged chunks which are not complete. 
If you want to center the time mean on the time period, you can activate the ``center_time=True`` flag.
This is at the moment only available yearly averages.

..  note ::
    The ``time_bounds`` boolean flag can be activated to build time bounds in a similar way to CMOR standard.
    By default, ``time_bounds`` is set to False.

Spatial Averaging
-----------------

When we instantiate the ``Reader`` object, grid areas for the source files are computed if not already available. 
After this, we can use them for spatial averaging using the ``fldmean()`` method, obtaining time series of global (field) averages.
For example, if we run the following commands:

.. code-block:: python

    tprate = data.tprate
    global_mean = reader.fldmean(tprate)

we get a time series of the global average ``tprate``.

It is also possible to apply a regional section to the domain before performing the averaging:

.. code-block:: python

    tprate = data.tprate
    global_mean = reader.fldmean(tprate, lon_limits=[-50, 50], lat_limits=[-10,20])

.. warning ::
    In order to apply an area selection the data Xarray must include ``lon`` and ``lat`` as coordinates.
    It can work also on unstructured grids, but information on coordinates must be available.
    If the dataset does not include these coordinates, this can be achieved with the fixer
    described in the :ref:`fixer` section.


Streaming of data
-----------------

.. _accessors:
Accessors
---------

Parallel Processing
-------------------

Graphic tools
-------------
