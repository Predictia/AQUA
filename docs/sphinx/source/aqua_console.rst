.. _aqua-console:

Configuration and Catalogue manager
===================================

Since ``v0.9`` the possibility to manage where the configuration and catalogue files are stored has been added.
This is based on a command line interface which can also handle fixes and grids files. 
Here we give a brief overview of the features.
If you are a developer, you may want to read the :ref:`dev-notes` section.

The entry point for the console is the command ``aqua``.
It has the following subcommands:

- :ref:`aqua-install`
- :ref:`aqua-add`
- :ref:`aqua-list`
- :ref:`aqua-update`
- :ref:`aqua-remove`
- :ref:`aqua-set`
- :ref:`aqua-uninstall`
- :ref:`aqua-fixes`
- :ref:`aqua-grids`

To show the AQUA version, you can use the command:

.. code-block:: bash

    aqua --version

while a brief help is available with:

.. code-block:: bash

    aqua --help, -h

It is possible to set the level of verbosity with two options:

.. option:: --verbose, -v

    It increases the verbosity level, setting it to INFO.

.. option:: --very-verbose, -vv

    It increases the verbosity level, setting it to DEBUG.

In both cases the level of verbosity has to be specified before the command.

.. _aqua-install:

aqua install
------------

With this command the configuration file and the default data models, grids and fixes are copied to the destination folder.
By default, this will be ``$HOME/.aqua``. It is possible to specify from where to copy and where to store.
It is also possible to ask for an editable installation, so that only links are created, ideal for developers, 
which can keep their catalog or fixes files under version control.

.. option:: --path, -p <path>

    The folder where the configuration file is copied to. Default is ``$HOME/.aqua``.
    If this option is used, the tool will ask the user if they want a link in the default folder ``$HOME/.aqua``.
    If this link is not created, the environment variable ``AQUA_CONFIG`` has to be set to the folder specified.

.. option:: --editable, -e <path>

    It installs the configuration file from the path given.
    It will create a symbolic link to the configuration folder.
    This is very recommended for developers. Please read the :ref:`dev-notes` section.

.. warning::
    The editable mode requires a path to the ``AQUA/config`` folder, not to the main AQUA folder.

.. _aqua-add:

aqua add <catalogue>
--------------------

This command adds a catalogue to the list of available catalogues.
It will copy the catalogue folder and files to the destination folder.
As before, it is possible to specify if symbolic links have to be created
and it is possible to install extra catalogues not present in the AQUA release.

.. option:: catalog

    The name of the catalogue to be added.
    It can be also a path pointing to a specific folder where an AQUA compatible catalog can be found
    This is a mandatory field.

.. option:: --editable, -e <path>

    It installs the catalogue based on the path given.
    It will create a symbolic link to the catalogue folder.
    This is very recommended for developers. Please read the :ref:`dev-notes` section.

.. _aqua-list:

aqua list
---------

This command lists the available catalogues in the installation folder.
It will show also if a catalogue is installed in editable mode.

.. option:: --all, -a

    This will show also all the fixes, grids and data models installed

.. _aqua-update:

aqua update <catalogue>
-----------------------

This command will check if there is a new version of the catalogue available and update it.

.. warning::

    This will work smoothly only for default AQUA catalogs unless the full path is specified.

.. _aqua-remove:

aqua remove <catalogue>
-----------------------

It removes a catalogue from the list of available catalogues.
This means that the catalogue folder will be removed from the installation folder or the link will be deleted
if the catalogue is installed in editable mode.

.. _aqua-set:

aqua set <catalogue>
--------------------

This command sets the default catalogue to be used.

.. warning::
    At the actual stage of development, the catalogue coincide with a machine.
    This command is then setting the machine name to be used in the configuration file.

.. _aqua-uninstall:

aqua uninstall
--------------

This command removes the configuration and catalogue files from the installation folder.
If the installation was done in editable mode, only the links will be removed.

.. note::
    If you need to reinstall aqua, the command ``aqua install`` will ask if you want to overwrite the existing files.

.. _aqua-fixes:

aqua fixes {add,remove} <fixes-file>
-------------------------------------

This submcommand is able to add or remove a fixes YAML file to the list of available installed fixes.
It will copy the fix file to the destination folder, or create a symbolic link if the editable mode is used.
This is useful if a new external fix is created and needs to be added to the list of available fixes.

.. option:: <fix-file>

    The path of the file to be added.
    This is a mandatory field.

.. option:: -e, --editable

    It will create a symbolic link to the fix folder. Valid only for ``aqua fixes add``

.. _aqua-grids:

aqua grids {add,remove} <grid-file>
-----------------------------------

This submcommand is able to add or remove a grids YAML file to the list of available installed grids.
It will copy the grids file to the destination folder, or create a symbolic link if the editable mode is used.
This is useful if new external grids are created and need to be added to the list of available grids.

.. option:: <grid-file>

    The path of the file to be added.
    This is a mandatory field.

.. option:: -e, --editable

    It will create a symbolic link to the grid folder. Valid only for ``aqua grids add``