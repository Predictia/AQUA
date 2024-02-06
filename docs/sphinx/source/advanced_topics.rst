.. _advanced-topics:
Advanced Topics
===============

.. _new-machine:
Adding a new machine
--------------------

Creation on the catalogue
^^^^^^^^^^^^^^^^^^^^^^^^^

Download of grids
^^^^^^^^^^^^^^^^^

Grids used in AQUA are stored and available on Swift storage, powered by DKRZ.
A command line tool is available to download the grids from Swift on your machine.

Please refer to the section :ref:`grids-downloader` for more details.

.. _FDB_dask:
Dask access to FDB or GSV
--------------------------

If an appropriate entry has been created in the catalogue, the reader can also read data from a FDB/GSV source. 
The request is transparent to the user (no apparent difference to other data sources) in the call.

.. code-block:: python

    reader = Reader(model="IFS", exp="control-1950-devcon", source="hourly-1deg")
    data = reader.retrieve(var='2t')

The default is that this call returns a regular dask-enabled (lazy) ``xarray.Dataset``,
like all other data sources.
This is performed by an intake driver for FDB which has been specifically developed from scratch inside AQUA.

In the case of FDB access specifying the variable is compulsory,
but a list can be provided and it is done for the FDB sources available in the catalogue.
If not specified, the default variable defined in the catalogue is used.

.. warning::
    The FDB access can be significantly fasten by selecting variables and time range.

An optional keyword, which in general we do **not** recommend to specify for dask access, is ``aggregation``,
which specifies the chunk size for dask access.
Values could be ``D``, ``M``, ``Y`` etc. (in pandas notation) to specify daily, monthly and yearly aggregation.
It is best to use the default, which is already specified in the catalogue for each data source.
This default is based on the memory footprint of single grib message, so for example for IFS-NEMO dative data
we use ``D`` for Tco2559 (native) and "1deg" streams, ``Y`` for monthly 2D data and ``M`` for 3D monthly data.
In any case, if you use multiprocessing and run into memory troubles for your workers, you may wish to decrease
the aggregation (i.e. chunk size).

.. _iterators:
Iterator access to data
-----------------------

In alternative to the lazy access it is also possible to ask the reader to return an *iterator/generator* object passing the ``stream_generator=True`` 
keyword to the ``retrieve()`` method.
In that case the next block of data can be read from the iterator with ``next()`` as follows:

.. code-block:: python

    reader = Reader(model="IFS", exp="fdb-tco399", source="fdb-long", aggregation="D",
                    regrid="r025")
    data = reader.retrieve(startdate='20200120', enddate='20200413', var='ci',
                           stream_generator=True)
    dd = next(data)

or with a loop iterating over ``data``. The result of these operations is in turn a regular xarray.Dataset containg the data.
Since this is a data stream the user should also specify the desired initial time and the final time (the latter can be omitted and will default to the end of the dataset).
When using an iterator it is possible to specify the size of the data blocks read at each iteration with the ``aggregation`` keyword
(``M`` is month, ``D``is day etc.). 
The default is ``S`` (step), i.e. single saved timesteps are read at each iteration.

Please notice that the resulting object obtained at each iteration is not a lazy dask array, but is instead entirely loaded into memory.
Please consider memory usage in choosing an appropriate value for the ``aggregation`` keyword.
