Configuration
=============

AQUA configuration is based on a configuration folder `config` which includes a few different files, both local and machine-dependent. 
The `config.yml` includes the most important path to be stored.

Then, machine-dependent folders are used to specify the properties of the data access and of the AQUA functions, as the interpolation features.

The `config` folder is structured as follows:


.. code-block:: text

    ├── config
    │   ├── data_models
    │   ├── fixes
    │   └── machines
    ├── config.yaml
    
In the `config.yaml` file, the following paths are specified:

.. code-block:: yaml

    machine: levante # machine name, AQUA will look for a folder with the same name in the machines folder

    reader: # path to the reader configuration file
      catalog: '{configdir}/machines/{machine}/catalog.yaml'
      regrid: '{configdir}/machines/{machine}/regrid.yaml'
      fixer: '{configdir}/fixes'

    cdo: # path to the cdo executable, that is necessary for generation interpolation weights
      levante: /sw/spack-levante/cdo-2.0.6-jkuh4i/bin/cdo
      lumi: /scratch/project_465000454/devaraju/SW/LUMI-22.08/C/python-xarray/bin/cdo


