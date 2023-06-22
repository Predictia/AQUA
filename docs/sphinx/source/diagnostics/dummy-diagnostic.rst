Dummy Diagnostic
================

Description
-----------

Dummy diagnostic provides an example on how diagnostics of the AQUA framework should be organised and written.
In this case the dummy diagnostic reads a field a computes the global mean using the fldmean method from the reader according to...
In particular, this documentation provides an example on how a diagnostic developer should write documentation about his/her diagnostic,
covering a short description of its contents and of its scientific basis. 
In case the diagnostic is bae on some already published material it is strongly 
recommended to include references to the inherent literature (we have a reference list below).
Please try to adhere to the following scheme as far as possible.

Input variables
---------------

* `tprate` (total precipitation rate, GRIB paramid 260048)
* `2t`     (2 metre temperature, GRIB pramid 167)

Output 
------

List here types of files/datasets produced by the diagnostic

Methods used
---------------

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
