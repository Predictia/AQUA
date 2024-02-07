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
  There is the possibility of specifing a `parent` fix so that a fix can be re-used with minor correction,
  merging small change to a larger ``fixer_name``.
- Using the source-based definition.
  Each source can have its own specific fix, or alternatively a ``default.yaml`` that can be used in the case of necessity.
  Please note that this is the older AQUA implementation and will be deprecated in favour of the new approach described above.

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
  (like ``mtpr`` in kg m-2 s-1). (See :ref:`metadata-fix` for more details)
- using the ``metpy.units`` module, it is capable of guessing some basic conversions.
  In particular, if a density is missing, it will assume that it is the density of water and will take it into account.
  If there is an extra time unit, it will assume that division by the timestep is needed. 

.. _fix-structure:
Fix structure
^^^^^^^^^^^^^

Here we show an example of a fixer file:

.. code-block:: yaml

    fixer_name:
        documentation-fix:
            method: replace
            data_model: ifs
            coords:
                time:
                    source: time-to-rename
            deltat: 3600 # Decumulation info
            jump: month
            vars:
                2t:
                    source: 2t
                    attributes: # new attribute
                        donald: 'duck'
                mtntrf: # Auto unit conversion from eccodes
                    derived: ttr
                    grib: true
                    decumulate: true     
                2t_increased: # Simple formula
                    derived: 2t+1.0
                    grib: true
                # example of derived variable, should be double the normal amount
                mtntrf2:
                    derived: ttr+ttr
                    src_units: J m-2 # Overruling source units
                    decumulate: true  # Test decumulation
                    units: "{radiation_flux}" # overruling units
                    attributes:
                        # assigning a long_name
                        long_name: Mean top net thermal radiation flux doubled
                        paramId: '999179' # assigning an (invented) paramId

We put together many different fixes, but let's take a look at the 
different sections of the fixer file.

- **documentation-fix**: This is the name of the fixer.
  It is used to identify the fixer and will be used in the entry metadata
  to specify which fixer to use. (See :ref:`add-data` for more details)
- **method**: This is the method used to fix the data.
  Available methods are:
    - **replace**: use the fixes overriding the default ones ``<MODEL_NAME>-default``.
      If you do not specify anything, this is the basic behaviour.
    - **merge**: merge the fixes with the default ones, with priority for the former.
      It can be used if the most of fixes from default are good,
      but something different in the specific source is required.
- **data_model**: the name of the data model for coordinates. (See :ref:`coord-fix`).
- **coords**: extra coordinate handling if data model is not flexible enough.
  (See :ref:`coord-fix`).
- **decumulation**: ``deltat`` and ``jump`` are defined to instruct the Reader
  decumulator about how to treat variables if we set ``decumulate: true``
- **vars**: this is the main fixer block, described in detail on the following section :ref:`metadata-fix`.

.. _metadata-fix:
Metadata Correction
^^^^^^^^^^^^^^^^^^^^

The **vars** block in the ``fixer_name`` is a list of variables that need
metadata correction.
This can be specified with all the available variables that a model can output.
The Reader will then apply fixes only to variables that are found in the specific
dataset, promoting the creation of a generic ``fixer_name`` that can be applied to every new
simulation more than a pletora of small specific fixes.

The section :ref:`fix-structure` provides an exhaustive list of cases.
It is possible to rename a variable according to GRIB2 standard, letting eccodes
handle the units and metadata modification or it is possible to write a
custom variable, with custom metadata and units override, as shown in the section above.

.. warning ::
    Recursive fixes (i.e. fixes of fixes) cannot be implemented.

.. _coord-fix:
Data Model and Coordinates Correction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The fixer can adopt a common *coordinate data model*
(default is the CDS data model).
If this data model is not appropriate for a specific source,
it is possible to specify a different one in the catalogue.

If the data model coordinate treatment is not enough to fix the coordinates,
it is possible to specify a custom fix in the catalogue in the **coords** block
as shown in section :ref:`fix-structure`.
For example, if the longitude coordinate is called ``longitude`` instead of ``lon``,
it is possible to specify a fix like:

.. code-block:: yaml

    lon:
        source: longitude

This will rename the coordinate to ``lon``.

.. note::
    When possible, prefer a **data model** treatment of coordinates and use the **coords**
    block as second option.

Time Aggregation
----------------

Input data may not be available at the desired time frequency. It is possible to perform time averaging at a given
frequency by using the ``timmean`` method. 

.. code-block:: python

    reader = Reader(model="IFS", exp="tco2559-ng5", source="ICMGG_atm2d")
    data = reader.retrieve()
    daily = reader.timmean(data, freq='daily')

Data have now been averaged at the desired daily timescale.

Some extra options are available:

- ``exclude_incomplete=True``: this flaf will remove averaged chunks which are not complete
  (for example, be sure that all the months are complete before doing the time mean).
- ``center_time=True``: this flag will center the time mean on the time period.
  At the moment available only for monthly and yearly time aggregation.
- ``time_bounds=True``: this flag can be activated to build time bounds in a similar way to CMOR standard.

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

.. _time-selection:
Time selection
--------------

Even if slicing your data after the ``retrieve()`` method is an easy task,
being able to perform a time selecetion during the Reader initialization
can speed up your code, having less metadata to explore.
For this reason ``startdate`` and ``enddate`` options are available both
during the Reader initialization and the ``retrieve()`` method to subselect
immediatly only a chunck of data.

.. note::
    If you're streaming data check the section :ref:`streaming` to have an
    overview of the behaviour of the Reader with these options.

.. _lev-selection:
Level selection
---------------

Similarly to :ref:`time-selection`, level selection is a trivial operation,
but when dealing with high-resolution 3D datasets, only ask for the
required levels can speed up the retrieve process.

When reading 3D data it is possible to specify already during ``retrieve()``
which levels to select using the ``level`` keyword.
The levels are specified in the same units as they are stored in the archive
(for example in hPa for atmospheric IFS data,
but an index for NEMO data in the FDB archive).

.. note::
    In the case of FDB data this presents the great advantage that a significantly reduced request will be read from the FDB 
    (by default all levels would be read for each timestep even if later a ``sel()`` or ``isel()`` selection
    is performed on the XArray).

.. warning::
    If you're dealing with level selection and regridding, please take a look at 
    the section :ref:`lev-selection-regrid`.

.. _streaming:
Streaming of data
-----------------

The Reader class includes the ability to simulate data streaming to retrieve chunks
of data of a specific time length.

Basic usage
^^^^^^^^^^^

To activate the streaming mode the user should specify the argument ``streaming=True``
in the Reader initialization.
The user can also choose the length of the data chunk with the ``aggregation`` keyword
(in pandas notation ``D``, ``M``, ``Y``, or ``daily``, ``monthly`` etc. or ``days``, ``months`` etc.).
The default is ``S`` (step), i.e. single saved timesteps are read at each iteration.
The user can also specify the desired initial and final dates with the keywords ``startdate`` and ``enddate``.

If, for example, we want to stream the data every three days from ``'2020-05-01'``, we need to call:

.. code-block:: python

    reader = Reader(model="IFS", exp= "tco2559-ng5", source="ICMGG_atm2d",
                    streaming=True, aggregation = '3D', startdate = '2020-05-01')    
    data = reader.retrieve()

The data available with the first retrieve will be only 3 days of the available times.
The ``retrieve()`` method can then be called multiple times,
returning a new chunk of 3 days of data, until all data are streamed.
The function will automatically determine the appropriate start and end points for each chunk based on
the internal state of the streaming process.

If we want to reset the state of the streaming process, we can call the ``reset_stream()`` method.

Iterator streaming
^^^^^^^^^^^^^^^^^^

Another possibility to deal with data streaming is to use the argument
``stream_generator=True`` in the Reader initialization:

.. code-block:: python

    reader = Reader(model="IFS", exp= "tco2559-ng5", source="ICMGG_atm2d",
                    stream_generator = 'True', aggregation = 'monthly')
    data_gen = reader.retrieve()
    
``data_gen`` is now a generator object that yields the requested one-month-long chunks of data
(See :ref:`iterators` for more info).
We can do operations with them by iterating on the generator object like:

.. code-block:: python

    for data in data_gen:
        # Do something with the data

.. _accessors:
Accessors
---------

AQUA also provides a special ``aqua`` accessor to Xarray which allows
to call most functions and methods of the reader
class as if they were methods of a DataArray or Dataset.

Basic usage
^^^^^^^^^^^

Reader methods like ``reader.regrid()`` or functions like ``plot_single_map()``
can now also be accessed by appending the suffix ``aqua`` to a
DataArray or Dataset, followed by the function of interest,
like in ``data.aqua.regrid()``.

This means that instead of writing:

.. code-block:: python

    reader.fldmean(reader.timmean(data.tcc, freq="Y"))

we can write:

.. code-block:: python

    data.tcc.aqua.timmean(freq="Y").aqua.fldmean()

.. note::
    The accessor always assumes that the Reader instance to be used is either
    the one with which a Dataset was created or, for new derived objects and for **DataArrays of a Datasets**,
    the last instantiated Reader or the last use of the ``retrieve()`` method.
    This means that if more than one reader instance is used (for example to compare different datasets)
    we recommend not to use the accessor.

Usage with multiple Reader instances
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As an alternative the Reader class contains a special ``set_default()`` method which sets that reader
as an accessor default in the following.
The accessor itself also has a ``set_default()`` method
(accepting a reader instance as an argument) which sets the default and returns the same object.

Usage examples when multiple readers are used:

.. code-block:: python

    from aqua import Reader
    reader1=Reader(model="IFS", exp="test-tco79", source="short", regrid="r100")  # the default is now reader1
    reader2=Reader(model="IFS", exp="test-tco79", source="short", regrid="r200")  # the default is now reader2
    data1 = reader1.retrieve()  # the default is now reader1 
    data2 = reader2.retrieve()  # the default is now reader2
    reader1.set_default()  # the default is now reader1 
    data1r = data1.aqua.regrid()
    data2r = data2.aqua.regrid()  # data2 was created by retrieve(), so it remembers its default reader
    data2r = data2['2t'].aqua.set_default(reader2).aqua.regrid()  # the default is set to reader2 before using a method

Parallel Processing
-------------------

Since most of the objects in AQUA are based on ``xarray``, you can use parallel processing capabilities provided by 
``xarray`` through integration with ``dask`` to speed up the execution of data processing tasks.

For example, if you are working with AQUA interactively
in a Jupyter Notebook, you can start a dask cluster to parallelize your computations.

.. code-block:: python

    from dask.distributed import Client
    import dask
    dask.config.config.get('distributed').get('dashboard').update({'link':'{JUPYTERHUB_SERVICE_PREFIX}/proxy/{port}/status'})

    client = Client(n_workers=40, threads_per_worker=1, memory_limit='5GB')
    client

The above code will start a dask cluster with 40 workers and one thread per worker.

AQUA also provides a simple way to move the computation done by dask to a compute node on your HPC system.
The description of this feature is provided in the section :ref:`slurm`.

Graphic tools
-------------
