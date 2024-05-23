.. _aqua-console:

Configuration and Catalogue manager
===================================

Since v0.8.2 the possibility to manage where the configuration and catalogue files are stored has been added.
Here we give a brief overview of the features.
If you are a developer, you may want to read the :ref:`dev-notes` section.

The entry point for the console is the command ``aqua``.
It has the following subcommands:

- :ref:`aqua-init`
- :ref:`aqua-add`
- :ref:`aqua-list`
- :ref:`aqua-update`
- :ref:`aqua-remove`
- :ref:`aqua-uninstall`

All the subcommands have the following option:

.. option:: --loglevel, -l <loglevel>

    The log level. Default is ``WARNING``.

While it is possible to check the version of the package with the following option:

.. option:: --version, -v

    Print the version of the package and exit.

.. _aqua-init:

aqua install
---------

With this command the configuration file ``config-aqua.yaml`` is copied from the package to the destination folder.

.. option:: --path, -p <path>

    The folder where the configuration file is copied to. Default is ``$HOME/.aqua``.

.. warning::
    If another folder is specified, the environment variable ``AQUA_CONFIG`` has to be set to that folder.

.. option:: --grids, -g <path>

    The folder where the grid files are stored. If defined it overrides the configuration file setting.

.. _aqua-add:

aqua add <catalogue>
--------------------

This command adds a catalogue to the list of available catalogues.
It will copy the catalogue file to the destination folder.

.. option:: catalog

    The name of the catalogue to be added.

.. warning::
    At the moment only catalogues present in the package can be added.
    This will change in the future, but for now the only way to add a new catalogue is in the editable mode.

.. option:: --editable, -e <path>

    It installs the catalogue based on the path given.
    It will create a symbolic link to the catalogue folder.
    This is very recommended for developers. Please read the :ref:`dev-notes` section.

.. _aqua-list:

aqua list
---------

This command lists the available catalogues in the installation folder.

.. _aqua-update:

aqua update <catalogue>
-----------------------

This command will check if there is a new version of the catalogue available and update it.

.. warning::
    This command is not yet implemented.

.. _aqua-remove:

aqua remove <catalogue>
-----------------------

It removes a catalogue from the list of available catalogues.
This means that the catalogue folder will be removed from the installation folder.

.. _aqua-uninstall:

aqua uninstall
--------------

This command removes the configuration and catalogue files from the installation folder.