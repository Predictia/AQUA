.. _add-data:
Adding new data
===============

To add your data to AQUA, you have to provide an ``intake`` catalogue that describes your data,
and in particular, the location of the data. 
This can be done in two different way, by adding a standard entry in the form of files
or using the specific AQUA FDB interface. 
Finally, to exploit of the regridding functionalities, you will also need to configure the machine-dependent
``regrid.yaml``. 

The 3-level hierarchy on which AQUA is based, i.e. model - exp - source, must be respected so that 
specific files must be created within the catalog of a specific machine.
How to create a new source and add new data is documented in the next sections.
