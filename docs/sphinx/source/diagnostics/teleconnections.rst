Teleconnections diagnostic
==========================

This package provides a diagnostic for teleconnections.

Overview of available functionalities
-------------------------------------

The diagnostic is available in the `teleconnections` folder inside the `diagnostics` folder.
The core functions developed for the diagnostic are available in the `index.py` file.
These functions can be run in a notebook or in a script.
Examples of the usage of the functions are available in the `notebooks` folder, both for ERA5 and nextGEMS cycle3 data.
Please notice that data necessary to run the diagnostic are not available in the repository. 
You will need to be on levante to be able to run by yourself the notebooks.

Teleconnections available:

- NAO: notebook available `diagnostics/teleconnections/notebooks/NAO.ipynb`
- ENSO: notebook available `diagnostics/teleconnections/notebooks/ENSO_nino3.4.ipynb`

More diagnostics or functionalities can be added in the future.
A configuration file is available in the `config` folder.
It can be customized to add new teleconnections or to change the default parameters of the diagnostic.

How to run the diagnostic
-------------------------

The diagnostic can be run in a notebook or in a script.
The following steps are necessary to run the diagnostic (we're taking the NAO as an example):

1. Import the necessary functions from the `index.py` file and from the `AQUA` framework.

.. code-block:: python

  from aqua import Reader
  from index import station_based_index
  from plots import index_plot
  from tools import load_namelist

Please notice that at the moment in order to import the functions from the `index.py` file,
the `teleconnections` folder needs to be in the same folder as the notebook or script.
A possible hack is to use `sys.path.append` to add the `teleconnections` folder to the path.
An example is available in the `notebooks` folder.

2. Load the config specific of your teleconnection.

.. code-block:: python
  
  diagname  = 'teleconnections'
  telecname = 'NAO'

  config = load_namelist(diagname)
  field = namelist[telecname]['field']

Without any argument, the `load_namelist` function will load the default config file, trying to get the correct path.

The dictionary extracted from the config file will be used to set the parameters of the diagnostic.
For NAO:

.. code-block:: yaml
  
  # NAO coordinates
  NAO:
    field: msl
    lat1: 37.7
    lon1: -25.7
    lat2: 64.1
    lon2: -22

Please notice that the `field` parameter is the name of the field in the data.
It may be different for different datasets and fix features available in the `AQUA` framework may be needed to automatize the access to data.

3. Load the data

Reader is a class of the AQUA framework that can be used to load the data.
It has to be initialized with the details of the data to be loaded.

.. code-block:: python
  
  model = 'IFS'
  exp = 'tco1279-orca025-cycle3'
  source = '2D_monthly_native'

  reader = Reader(model=model,exp=exp,source=source,regrid='r025')

Regrid of the data, time aggregation and fix features may be needed to automatize and simplify the access to data.
Check the `AQUA` framework documentation for more details.
What is needed to run the diagnostic is a `xarray.Dataarray` object with the data to be used.

4. Run the diagnostic

.. code-block:: python
  
  nao = station_based_index(field=infile,namelist=namelist,telecname=telecname)

5. Plot the results

Some plot functions are available in the `plots.py` file.
Optionally, the `xarray.Dataarray` object returned by the `station_based_index` function can be used to plot the results in any way,
to save the results in a file or to do any other operation.
