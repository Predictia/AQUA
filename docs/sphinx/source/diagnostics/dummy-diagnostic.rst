Dummy Diagnostic
================

Description
-----------

Dummy diagnostic is a simple diagnostic that does nothing.
This documentation is an empty placeholder to remind you to write some documentation for your diagnostic.
This section should contain a short description of the contents of the diagnostic and of its scientific basis. 
It can contain references to literature (we have a reference list below).
Please try to adhere to the following scheme as far as possible.

Input variables
---------------

* `tprate` (total precipitation rate, GRIB paramid 260048)
* `2t`     (2 metre temperature, GRIB pramid 167)

Output 
------

Nothing in this case. List here types of files/datasets produced by the diagnostic

Observations
------------

If relevant, list the observational datasets used by this diagnostic (e.g. for validation/comparison)

References
----------

* E. Empty, D. Dummy et al. (2023) The art of saying nothing. Emptyness, 1: 0-1. `DOI <http://doi.org/00.0000/e-00000-000.xxxx>`_


Example Plot(s)
---------------

.. figure:: figures/dummy-diagnostic1.png
    :width: 10cm

    An illustration of the big void left by this diagnostic

Available demo notebooks
------------------------

Notebooks are stored in diagnostics/dummy-diagnostic/notebooks

* `dummy.ipynb <https://github.com/oloapinivad/AQUA/blob/main/diagnostics/dummy-diagnostic/notebooks/dummy.ipynb>`_
        
Detailed API
------------

This section provides a detailed reference for the Application Programming Interface (API) of the "dummy" diagnostic,
produced from the diagnostic function docstrings.

.. automodule:: dummy
    :members:
    :undoc-members:
    :show-inheritance:
