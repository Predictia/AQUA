Installation
============

This document provides detailed installation instructions for the Python package AQUA, 
which has been tested on Python 3.9 and 3.10. We recommend using Mamba, a package manager
for conda-forge, for the installation process.

.. contents::
   :local:
   :depth: 1

Prerequisites
-------------

Before installing AQUA, ensure that you have the following prerequisites installed:

- `Git <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`_
- `Mamba <https://github.com/mamba-org/mamba>`_ or `Conda <https://docs.conda.io/projects/conda/en/latest/user-guide/install/>`_

.. note ::
   Currently, AQUA is a private repository so that you need to be registered as a user to get access to it.

Creating a Conda/Mamba Environment and Installing Packages
----------------------------------------------------------

Clone the AQUA repository from GitHub:

.. code-block:: bash
   
   git clone https://github.com/oloapinivad/AQUA.git

Change to the AQUA directory:

.. code-block:: bash
   
   cd AQUA

Create a new Mamba environment and install the required packages using the provided environment.yml file:

.. code-block:: bash
   
   mamba env create -f environment.yml

Activate the newly created aqua environment:

.. code-block:: bash
   
   conda activate aqua

At this point, you should have successfully installed the AQUA package and its dependencies 
in the newly created aqua environment.

If you are not working on Levante, remember to change the machine name in the `config/config.yaml` file:

.. code-block:: markdown
   
   machine: levante

If you are usig LUMI, there is a script available providing an installation of the correct environment. You just have to run:

.. code-block:: bash

   ./config/machines/lumi/installation/lumi_install.sh
