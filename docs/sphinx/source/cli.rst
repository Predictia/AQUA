.. _cli:
Command Line Interface tools
============================

This sections describes the series of Command Line Interface (CLI) tools currently available in AQUA.
It includes software with a variety of goals, which are mostly made for advanced usage. 

.. _aqua_analysis:
AQUA analysis wrapper
---------------------

A wrapper containing calls to all the state-of-the-art diagnostic available in AQUA
is provided in the ``cli/aqua-analysis/`` folder.

Basic usage:

.. code-block:: bash

    bash aqua-analysis.sh

.. _fdb-catalog-generator:
Catalog entry generator for FDB sources
---------------------------------------

This tool, currently under development, will provide the generation of the FDB sources for the Climate DT project.


.. _gribber:
GRIB catalog generator
----------------------

A tool building on Gribscan, aiming at creating compact catalog entries through JSON files for massive GRIB archives.
A script in the ``cli/gribber`` folder is available.

.. warning ::

    This tool is currently deprecated, it might be removed in the future.


.. _grids-from-data:
Generation of grid from data
----------------------------

A tool to create CDO-compliant grid files (which are fundamental for proper regridding) specifically 
for oceanic model in order to ensure the right treatment of masks. 
Two scripts in the the ``cli/grid-fromd-data`` folder are available.

Both ``hpx-from-source.py`` and ``multiIO-from-source.py`` works starting from specific sources, 
saving them to disk and processing the final results with CDO to ensure the creation
of CDO-compliant grid files that can be later used for areas and remapping computation.

A YAML configuration file must be specified.

Basic usage:

.. code-block:: bash

    ./hpx-from-source.py -c config-hpx-nemo.yaml -l INFO

.. _grids-downloader:
Grids downloader
----------------

The grids used in AQUA are available for download.
A script in the ``cli/grids-downloader/`` folder is available

Basic usage:

.. code-block:: bash

    bash grids-downloader.sh all

This will download all the grids used in AQUA.
It is also possible to download only a subset of the grids,
by specifying the group of grids to download (usually one per model).

LUMI container installation
---------------------------

Includes the script for the installation of the container on LUMI: please refer to :ref:`container`

LUMI conda installation
-----------------------

Includes the script for the installation of conda environment on LUMI: please refer to :ref:`installation-lumi`

.. _orca:
ORCA grid generator
-------------------

A tool to generate ORCA grid files (with bounds) from the `mesh_mask.nc`. 
A script in the ``cli/orca-grids`` folder is available.

Basic usage:

.. code-block:: bash

    ./orca_bounds_new.py mesh_mask.nc orcefile.nc

.. _weights:
Weights generator
-----------------

A tool to compute via script or batch job the generation of interpolation weights which are 
too heavy to be prepared from notebook or login node. It can be configured to run on all the 
catalog enties so that it can be used to update existing weights if necessary, or to compute 
all the weights on a new machine.
A script in the ``cli/generate_weights`` folder is available.

Basic usage:

.. code-block:: bash

    ./generate_weights.py -c weights_config.yaml


