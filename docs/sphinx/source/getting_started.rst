Getting started
===============

Installation
------------

If you open this page without having AQUA installed, please follow the instructions
given in the :ref:`installation` section before reading further.

Setting up your kernel for Jupyter
----------------------------------

You need to register the kernel for the aqua environment to work with the AQUA 
package in Jupyter Hub on HPC systems.

Activate the environment and register the kernel with the following command:

.. code-block:: bash

    mamba activate aqua
    python -m ipykernel install --user --name=aqua