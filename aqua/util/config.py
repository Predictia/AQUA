"""Utility functions for getting the configuration."""
import os
import sys
from .yaml import load_yaml


def get_config_dir(filename='config.yaml'):
    """
    Return the path to the configuration directory,
    searching in a list of pre-defined directories.

    Generalized to work for config files with different names.

    Args:
        filename (str): the name of the configuration file
                        Default is 'config.yaml'

    Returns:
        configdir (str): the dir of the catalog file and other config files

    Raises:
        FileNotFoundError: if no config file is found in the predefined folders
    """

    configdirs = []

    # if AQUA is defined
    aquadir = os.environ.get('AQUA')
    if aquadir:
        configdirs.append(os.path.join(aquadir, 'config'))

    # set of predefined folders to browse
    configdirs.extend(['./config', '../config', '../../config', '../../../config'])

    # if the home is defined
    homedir = os.environ.get('HOME')
    if homedir:
        configdirs.append(os.path.join(homedir, '.aqua', 'config'))

    # autosearch
    for configdir in configdirs:
        if os.path.exists(os.path.join(configdir, filename)):
            return configdir

    raise FileNotFoundError(f"No config file {filename} found in {configdirs}")


def get_machine(configdir):
    """
    Extract the name of the machine from the configuration file

    Args:
        configdir(str): the configuration file directory
     Returns:
        The name of the machine read from the configuration file
    """

    config_file = os.path.join(configdir, "config.yaml")
    if os.path.exists(config_file):
        base = load_yaml(os.path.join(configdir, "config.yaml"))
        return base['machine']
    else:
        sys.exit('Cannot find the basic configuration file!')


def get_reader_filenames(configdir, machine):
    """
    Extract the filenames for the reader for catalog, regrid and fixer

    Args:
        configdir(str): the configuration file directory
        machine(str): the machine on which you are running
     Returns:
        Three strings for the path of the catalog, regrid and fixer files
    """

    config_file = os.path.join(configdir, "config.yaml")
    if os.path.exists(config_file):
        base = load_yaml(os.path.join(configdir, "config.yaml"))
        catalog_file = base['reader']['catalog'].format(machine=machine,
                                                        configdir=configdir)
        if not os.path.exists(catalog_file):
            sys.exit(f'Cannot find catalog file in {catalog_file}')
        regrid_file = base['reader']['regrid'].format(machine=machine,
                                                      configdir=configdir)
        if not os.path.exists(regrid_file):
            sys.exit(f'Cannot find catalog file in {regrid_file}')
        fixer_folder = base['reader']['fixer'].format(machine=machine,
                                                      configdir=configdir)
        if not os.path.exists(fixer_folder):
            sys.exit(f'Cannot find catalog file in {fixer_folder}')

    return catalog_file, regrid_file, fixer_folder, config_file
