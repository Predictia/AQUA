Getting Started
===============

Installation
------------

If you open this page without having AQUA installed, please follow the instructions
given in the :ref:`installation` section before reading further.

Set up environment variables
----------------------------

To work with the AQUA package it is strongly recommended to set up an environment variable
to specify the path to the AQUA package. This can be done by adding the following line to
your `.bashrc` or `.bash_profile` file:

.. code-block:: bash

    export AQUA=/path/to/aqua

This will allow you to use the AQUA package from any location on the system and will make
clear for the code where to find the AQUA catalogue (see :ref:`catalogue`).

Set up configuration file
-------------------------

A configuration file is available to specify the parameters for the AQUA package.
This is a YAML file located in `config/config-aqua.yaml`.

The configuration file is used to specify the following parameters:

- **machine**: the machine on which the code is running. This is used to specify the
  location of the AQUA catalogue and the location of the data. Default is ``lumi``.
  Other options are ``ci`` and ``levante``. Custom machines can be defined (see :ref:`new-machine`).
- **cdo**: location of the CDO executable. By default this option is not needed, as CDO is required in the ``environment.yml`` file.

Set up Jupyter kernel
---------------------

You need to register the kernel for the aqua environment to work with the AQUA 
package in Jupyter Hub on HPC systems.

Activate the environment and register the kernel with the following command:

.. code-block:: bash

    mamba activate aqua
    python -m ipykernel install --user --name=aqua