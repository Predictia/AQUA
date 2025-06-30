.. _installation:

Installation
============

In this section we will provide a step-by-step guide to install the Python package AQUA.
AQUA is developed and tested with Python 3.12 and it supports Python 3.9 or later (with the exclusions of 3.13).

We recommend using Mamba/Conda package manager for the installation process.

.. note ::
    Soon AQUA will be available on the PyPI repository, so you will be able to install it with pip.
    The installation process will be updated accordingly.

Prerequisites
-------------

Before installing AQUA, ensure that you have the following software installed:

- `Git <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`_: AQUA is hosted on GitHub, and you will need Git to clone the repository.
- `Miniforge <https://github.com/conda-forge/miniforge>`_ : Miniforge is a package manager for conda-forge, and it is the recommended package manager for the installation process. 

.. _installation-conda:

Installation with Miniforge
---------------------------

First, clone the AQUA repository from GitHub:

.. code-block:: bash

    git clone git@github.com:DestinE-Climate-DT/AQUA.git

Then, navigate to the AQUA directory:

.. code-block:: bash

    cd AQUA

Create a new environment with Mamba.
An environment file is provided in the repository, so you can create the environment with the following command:

.. code-block:: bash

    conda env create -f environment.yml

This will create a new environment called ``aqua`` with all the required dependencies.

Finally, activate the environment:

.. code-block:: bash

    conda activate aqua

At this point, you should have successfully installed the AQUA package and its dependencies 
in the newly created aqua environment.

.. note ::
    Together with the environment file, a ``pyproject.toml`` file is provided in the repository.
    This file contains the required dependencies for the AQUA package and allows you to install the package with the pip package manager.
    However, we recommend using Conda to install the package and its dependencies, since some dependencies are not available in the PyPI repository.
    If you want to install the package with pip, please be aware that you may need to install some dependencies manually.

.. note ::
    If you need to access data written in an FDB database, you need to install the FDB5 library.
    The FDB5 library is not available in the conda-forge repository, so you need to install it manually.
    If you are working on a supported HPC, you can check the corresponding section for more information on if and where the FDB5 library is available.

Update of the environment
-------------------------

If you want to install AQUA in an existing environment, or if you want to update the environment with the latest version of the package,
you can install the dependencies with the following command:

.. code-block:: bash

    conda env update -n <environment_name> -f environment.yml

Replace ``<environment_name>`` with the name of the existing environment if this is different from ``aqua``.

.. _installation-lumi:


HPC Installation
----------------

Installation on LUMI HPC
^^^^^^^^^^^^^^^^^^^^^^^^

LUMI is currently the main HPC of the DestinE-Climate-DT project, and it is the main platform for the development of AQUA.
The Lustre filesystem does not support the use of conda environments, so another approach has been developed to install on LUMI,
based on `container-wrapper <https://docs.lumi-supercomputer.eu/software/installing/container-wrapper/>`_.

First, clone the AQUA repository from GitHub as described in the previous section.

For simpler installation, it is recommended to define an ``$AQUA`` environment variable that points to the AQUA directory:

.. code-block:: bash

    export AQUA=/path/to/AQUA

Then, navigate to the AQUA directory and specifically in the ``cli/lumi-install`` directory:

.. code-block:: bash

    cd $AQUA/cli/lumi-install

Run the installation script:

.. code-block:: bash

    ./lumi-install.sh

This installs the AQUA environment into a container, and then set up the correct modules
via a ``load_aqua.sh`` script that is generated and then called from the ``.bash_profile``.
The script will actually ask the user if they wish to include ``load_aqua.sh`` in ``.bash_profile`` at the end of the installation.
If you do not agree, you will need to call ``load_aqua.sh`` manually every time you want to use AQUA.

.. note ::
    The installation script is designed to be run on the LUMI cluster, and it may require some adjustments to be run on other systems
    that use the container-wrapper tool. Please refer to the documentation of the container-wrapper tool for more information.

.. warning ::
    This installation script, despite the name, does not install the AQUA package in the traditional sense nor in a pure container.
    It wraps the conda installation in a container, allowing to load LUMI modules and run from command line or batch jobs the AQUA code.
    Different LUMI module loading or setups may lead to different results, but it's the most flexible way to develop AQUA on LUMI.

.. note ::
    If you encounter any issues with the installation script, please refer to the :ref:`faq` section.

.. _installation-levante:

Installation on Levante HPC at DKRZ
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can follow the installation process described in the previous section (see :ref:`installation-conda`).
In order to use the FDB access, you need to load the FDB5 binary library (``libfdb5.so``).
At the moment a specific module for levante seems not to be available, so you can either compile your own copy and then make it available
(download the source code from `https://github.com/ecmwf/fdb <https://github.com/ecmwf/fdb>`_), or you can use our precompiled version by setting:

.. code-block:: bash

    export LD_LIBRARY_PATH=/work/bb1153/b382075/aqua/local/lib:$LD_LIBRARY_PATH 
    
in ``.bash_profile`` and in ``.bashrc`` in your home directory.

The GSV package will also require, in order to correctly decode the unstructured grid, an environment variable to be set:

.. code-block:: bash

    export GRID_DEFINITION_PATH=/work/bb1153/b382321/grid_definitions

This path is the one where the grid definitions are stored, and it is necessary for the GSV package to work correctly.
Also in this case, you can set the environment variable in your ``.bash_profile`` and in ``.bashrc`` in your home directory.

.. _installation-mn5:

Installation on MareNostrum 5 (MN5) HPC at BSC
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To enable internet-dependent operations like git, pip or conda on MN5, you can configure an SSH tunnel and set up proxy environment variables.

.. note::
    We recommend using a machine with a stable connection, such as Levante or LUMI, for these configurations, as connections to MN5 from personal computers may be unstable.

Add a ``RemoteForward`` directive with a valid port number under the MN5 section of your ``~/.ssh/config`` file.
Use the following configuration, replacing ``<port_number>`` with a unique port number to avoid conflicts
(on most systems the valid range for ports is from 1024 to 49151 for user-level applications).

.. code-block:: RST

    Host mn5
        RemoteForward <port_number>

After logging into MN5, export the following proxy environment variables to direct traffic through the SSH tunnel. 
Replace ``<port_number>`` with the same port number used in your SSH configuration:

.. code-block:: bash

    export https_proxy=socks5://localhost:<port_number>
    export http_proxy=socks5://localhost:<port_number>

You can add these exports to your ``.bash_profile`` and ``.bashrc`` files for persistence.

You can check if the forwarding is running by using the following command with your chosen port number:

.. code-block:: bash

    netstat -tlnp | grep <port_number>

Next, create your GitHub SSH key as usual, and then update your ``~/.ssh/config`` file with the following configuration:

.. code-block:: RST

    Host github.com
        Hostname ssh.github.com
        Port 443
        User git
        IdentityFile ~/.ssh/id_github
        ProxyCommand nc -x localhost:<port_number> %h %p

To verify the configuration, try testing the SSH connection with:

.. code-block:: bash

    ssh -T git@github.com

Once verified, you can successfully use ``git clone`` and other Git commands with SSH.

To install AQUA, see :ref:`installation-conda`.

.. warning::

   The ``wget`` command does not work properly in this setup. Use ``curl`` as an alternative for downloading files.


To use the FDB5 binary library on MN5, set the following environment variable:

.. code-block:: bash

    export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/gpfs/projects/ehpc01/sbeyer/models/DE_CY48R1.0_climateDT_tco399_aerosol_runoff/build/lib"


.. _installation-hpc2020:

Installation on ECMWF HPC2020
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

HPC2020 is moving to a more container-based approach, so the suggested installation process uses a technology similar to the one used on LUMI.
In fact, using directly conda or mamba on lustre filesystems (``$PERM`` and ``$HPCPERM``) is not recommended 
and has been verified to lead to severe performance issues.

The recommended approach is to use the `tykky module <https://docs.csc.fi/computing/containers/tykky/>`_ developed by CSC, and available on HPC2020, which provides
the same container wrapper technology used for an install on LUMI. 
This process is also described in the relevant HPC2020 `documentation pages <https://confluence.ecmwf.int/display/UDOC/Moving+away+from+Anaconda+and+Miniconda>`_.

While basically you could follow the instructions in the ECMWF docs on how to create a tykky environment, a small bug in one of the AQUA dependencies requires a slightly 
more complex procedure, so that, as for LUMI, a convenience installation script has been created.

First, clone the AQUA repository from GitHub as described in the previous section.

The installation process uses considerable resources which may exceed the capacity of the login node.
For this reason, it is recommended to start an interactive session asking for adequate resources:

.. code-block:: bash

    ecinteractive -c 8 -m 20 -s 30

which will ask for a session with 8 cpus, 20 GB of RAM and 30 GB of temporary local disk storage. This is required only for the installation, not necessarily for using AQUA.

.. note ::
    If this is the first time that you run ``ecinteractive``, you should first set up your ssh keys by running the command ``ssh-key-setup``.

It is recommended to define an ``$AQUA`` environment variable that points to the AQUA directory (the script will assume by default ``AQUA=$HPCPERM/AQUA``):

.. code-block:: bash

    export AQUA=/path/to/AQUA

Then run the the installation script:

.. code-block:: bash

    cd $AQUA/cli/hpc2020-install
    ./hpc2020-install.sh

The script installs by default the AQUA tykky environment in the directory ``$HPCPERM/tykky/aqua``.

The script will ask the user if they wish to add the AQUA environment  permanently to their ``$PATH`` in the ``.bash_profile`` file at the end of the installation.
Please note that adding AQUA to your PATH will make you use the aqua environment for all activities on HPC2020, so this is not really recommended.

Instead, the recommended way to use AQUA is by loading the environment with a conda-like syntax:

.. code-block:: bash
    
    module load tykky
    tykky activate aqua

You can later also use ``tykky deactivate`` to deactivate the environment.

In case you plan to use Visual Studio Code, you can add a kernel pointing to the containerized AQUA by running also the following command:

.. code-block:: bash

    $HPCPERM/tykky/aqua/bin/python3 -m ipykernel install --user --name=<my_containerised_env_name>


Installation and use of the AQUA container
------------------------------------------

In order to use AQUA in complicate workflows or in a production environment, it is recommended to use the AQUA container.
The AQUA container is a Docker container that contains the AQUA package and all its dependencies.

Please refer to the :ref:`container` section for more information on how to deploy and how to use the AQUA container.

.. note ::
    If you're working on LUMI, Levante or MN5 HPCs, a compact script is available to load the AQUA container,
    mounting the necessary folders and creating the necessary environment variables.
    Please refer to the :ref:`container` section.
