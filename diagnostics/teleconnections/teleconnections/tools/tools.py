'''
This module contains miscellaneous tools for the teleconnections diagnostic.
- loading functions, to deal with yaml files
'''

from aqua.util import load_yaml, get_config_dir


def load_namelist(diagname='teleconnections', configdir=None):
    """
    Load diagnostic yaml file.

    Args:
        diagname (str, opt):    diagnostic name. Default is 'teleconnections'
        configdir (str, opt):   path to config directory. Default is Nones

    Returns:
        namelist (dict):        Diagnostic configuration
    """
    if configdir is None:
        filename = f'{diagname}.yaml'
        configdir = get_config_dir(filename)

    infile = f'{configdir}/{diagname}.yaml'
    namelist = load_yaml(infile)

    return namelist
