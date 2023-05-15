Adding data to AQUA
===================

In order to add your data to AQUA, you have to provide intake catalog, that describe your data, 
and in particular the location of the data.

The best way to explain the proccess it is to follow the example of adding some fake dataset.

Let's imagine we have a dataset, called `yearly_SST`, that consist of:
- 2 netCDF files, each file contains 1 year of data (`/data/path/1990.nc` and `/data/path/1991.nc`)
- data are stored in 2D arrays, with dimensions `lat` and `lon`
- coordinate variables are `lat` and `lon` and one time variable `time`, all 1 dimensional
- data located on `levante` machine

We will create a catalog, that will describe this dataset, and then we will add it to AQUA. 
The simplest intake catalog, that describes this dataset, will look like this:

.. code-block:: yaml

    plugins:
    source:
        - module: intake_xarray

    sources:
      annual:
        description: my amasing yearly_SST dataset    
        driver: netcdf
        args:
            chunks:
                time: 1
            urlpath:
            - /data/path/1990.nc
            - /data/path/1991.nc

We name this catalog `yearly_SST.yaml` and save it in the `config/machines/levante/catalog/yearly_SST` directory (that we should create first).
We have to add another file to the `config/machines/levante/catalog/yearly_SST` directory, that is called `main.yaml`. 
In this file we just point to `yearly_SST.yaml`, but if we have several catalogs for the same dataset/model, we can point to all of them here.
In our case, the `main.yaml` file will look like this:

.. code-block:: yaml

    sources:
      yearly_sst:
        description: amazing yearly_SST dataset
        driver: yaml_file_cat
        args:
          path: "{{CATALOG_DIR}}/yearly_SST.yaml"


The next step is to add this catalog to the `config/machines/levante/catalogs.yaml` file. The additional entry in this file will look like this:

.. code-block:: yaml

    yearly_SST:
        description: amazing yearly_SST dataset
        driver: yaml_file_cat
        args:
          path: "{{CATALOG_DIR}}/yearly_SST/main.yaml"

The last thing to do is to add grid infromation about the data to the `config/machines/levante/regrid.yaml` file. In the `source_grids:`
section of the file we add the following entry:

.. code-block:: yaml

    yearly_SST:
        yearly_sst:
            default:
                space_coord: ["lon", "lat"]

The grid is regular and all the info contained inside, so there should be no problem for cdo to compute grid areas and interpolation weights.

Now we can access our dataset from AQUA with the following command:

.. code-block:: python

    from aqua import Reader
    reader = Reader(model="yearly_SST", exp="yearly_sst", source="annual", regrid='r100')
    data = reader.retrieve(fix=False)


You can also add fixes to your dataset by following examples in the `config/fixes/` directory.






