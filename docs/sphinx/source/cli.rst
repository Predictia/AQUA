.. _cli:
Command Line Interface tools
============================

AQUA analysis wrapper
---------------------

A wrapper containing calls to all the state-of-the-art diagnostic available in AQUA
is provided in the `cli/aqua-analysis/` folder.

.. _grids-downloader:
Grids downloader
----------------

The grids used in AQUA are available for download.
A script in the ``cli/grids-downloader/`` folder is available.

The basic usage is:

.. code-block:: bash

    source grids-downloader.sh all

This will download all the grids used in AQUA.
It is also possible to download only a subset of the grids,
by specifying the group of grids to download (usually one per model).
