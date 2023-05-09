Examples and Tutorials
======================

Jupyter Notebooks for Various Use Cases
---------------------------------------

AQUA provides a collection of Jupyter notebooks to help users explore and understand its capabilities, which are stored in `notebooks/reader` folder, and 
includes a range of use cases, from basic examples to advanced applications. Some example notebooks include:

1. `Introduction and main features <https://github.com/oloapinivad/AQUA/blob/main/notebooks/reader/main.ipynb>`_
2. `Regridding <https://github.com/oloapinivad/AQUA/blob/main/notebooks/reader/regrid.ipynb>`_
3. `Coordinate, variable name, units fixer <https://github.com/oloapinivad/AQUA/blob/main/notebooks/reader/fixer.ipynb>`_
4. `Temporal averaging  <https://github.com/oloapinivad/AQUA/blob/main/notebooks/reader/timmean.ipynb>>`_
5. `Spatial (field) averaging <https://github.com/oloapinivad/AQUA/blob/main/notebooks/reader/fldmean.ipynb>>`_
6. `Access to other datasets <https://github.com/oloapinivad/AQUA/blob/main/notebooks/reader/datasets.ipynb>>`_
7. `Streaming emulator <https://github.com/oloapinivad/AQUA/blob/main/notebooks/reader/streaming.ipynb>>`_

Tips and Best Practices
-----------------------

When using AQUA, consider the following tips and best practices to ensure optimal performance and usability:

1. Use a virtual environment to isolate the AQUA installation and its dependencies.
2. Familiarize yourself with xarray data structures and operations, as they form the basis of AQUA's data handling capabilities.
3. Always preprocess and regrid your data before running diagnostics to ensure consistent results.
4. Run diagnostics in parallel whenever possible to reduce computational time.
5. Use the provided Jupyter notebooks as a starting point for your own analyses, and customize them to suit your specific needs.
6. Consult the AQUA documentation and API reference for detailed information on available functions.
