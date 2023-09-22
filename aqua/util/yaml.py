"""YAML utility functions"""

import operator
import os
import re
import sys
from string import Template
import xarray as xr
from collections import defaultdict
from ruamel.yaml import YAML
from aqua.logger import log_configure


def load_multi_yaml(folder_path, definitions=None,
                    filename=None, **kwargs):
    """
    Load and merge all yaml files located in a given folder
    into a single dictionary.

    Args:
        folder_path(st or list):   The path of the folders containing the yaml
                                   files to be merged.
        definitions (str or dict, opt): name of the section containing string template
                                        definitions or a dictionary with the same
        filename (str, optional):   the name of the file to be merged.
                                    If None, all the yaml files in the folders will be merged.
                                    If a string is passed, only the yaml file with
                                    the matching name will be merged.

    Keyword Args:
        loglevel (str, optional): the loglevel to be used, default is 'WARNING'

    Returns:
        A dictionary containing the merged contents of all the yaml files.
    """
    yaml = YAML()  # default, if not specified, is 'rt' (round-trip)

    if isinstance(definitions, str):  # if definitions is a string we need to read twice
        yaml_dict = _load_merge(folder_path=folder_path, definitions=None,
                                filename=filename, **kwargs)  # Read without definitions
        definitions = yaml_dict.get(definitions)
        yaml_dict = _load_merge(folder_path, definitions,
                                filename=filename, **kwargs)  # Read again with definitions
    else:  # if a dictionary or None has been passed for definitions we read only once
        yaml_dict = _load_merge(folder_path, definitions,
                                filename=filename, **kwargs)

    return yaml_dict


def load_yaml(infile, definitions=None):
    """
    Load yaml file with template substitution

    Args:
        infile (str): a file path to the yaml
        definitions (str or dict, optional): name of the section containing string template
                                             definitions or a dictionary with the same
    Returns:
        A dictionary with the yaml file keys
    """

    if not os.path.exists(infile):
        raise ValueError(f'ERROR: {infile} not found: you need to have this configuration file!')

    yaml = YAML(typ='rt')  # default, if not specified, is 'rt' (round-trip)

    cfg = None
    # Load the YAML file as a text string
    with open(infile, 'r', encoding='utf-8') as file:
        yaml_text = file.read()

    if isinstance(definitions, str):  # if it is a string extract from original yaml, else it is directly a dict
        cfg = yaml.load(yaml_text)
        definitions = cfg.get(definitions)

    if definitions:
        # perform template substitution
        template = Template(yaml_text).safe_substitute(definitions)
        cfg = yaml.load(template)
    else:
        if not cfg:  # did we already load it ?
            cfg = yaml.load(yaml_text)

    return cfg


def dump_yaml(outfile=None, cfg=None, typ='rt'):
    """
    Dump to a custom yaml file

    Args:
        outfile(str):   a file path
        cfg(dict):      a dictionary to be dumped
        typ(str):       the type of YAML initialisation.
                        Default is 'rt' (round-trip)
    """
    # Initialize YAML object
    yaml = YAML(typ=typ)

    # Check input
    if outfile is None:
        raise ValueError('ERROR: outfile not defined')
    if cfg is None:
        raise ValueError('ERROR: cfg not defined')

    # Dump the dictionary
    with open(outfile, 'w', encoding='utf-8') as file:
        yaml.dump(cfg, file)


def eval_formula(mystring, xdataset):
    """Evaluate the cmd string provided by the yaml file
    producing a parsing for the derived variables"""

    # Tokenize the original string
    token = [i for i in re.split('([^\\w.]+)', mystring) if i]
    if len(token) > 1:
        # Special case, start with -
        if token[0] == '-':
            out = -xdataset[token[1]]
        else:
            # Use order of operations
            out = _operation(token, xdataset)
    else:
        out = xdataset[token[0]]
    return out


def _operation(token, xdataset):
    """Parsing of the CDO-based commands using operator package
    and an ad-hoc dictionary. Could be improved, working with four basic
    operations only."""

    # define math operators: order is important, since defines
    # which operation is done at first!
    ops = {
        '/': operator.truediv,
        "*": operator.mul,
        "-": operator.sub,
        "+": operator.add
    }

    # use a dictionary to store xarray field and call them easily
    dct = {}
    for k in token:
        if k not in ops:
            try:
                dct[k] = float(k)
            except ValueError:
                dct[k] = xdataset[k]

    # apply operators to all occurrences, from top priority
    # so far this is not parsing parenthesis
    code = 0
    for p in ops:
        while p in token:
            code += 1
            # print(token)
            x = token.index(p)
            name = 'op' + str(code)
            # replacer = ops.get(p)(dct[token[x - 1]], dct[token[x + 1]])
            # Using apply_ufunc in order not to
            replacer = xr.apply_ufunc(ops.get(p), dct[token[x - 1]], dct[token[x + 1]],
                                      keep_attrs=True, dask='parallelized')
            dct[name] = replacer
            token[x - 1] = name
            del token[x:x + 2]
    return replacer


def _load_merge(folder_path,
                definitions,
                filename=None,
                merged_dict=None,
                loglevel='WARNING'):
    """
    Helper function for load_merge_yaml.
    Load and merge yaml files located in a given folder
    into a single dictionary.

    It can merge specific file if a filename is provided
    and it can create a new dictionary or update an existing one,
    if merged_dict is provided.

    Args:
        folder_path(str or list):   The path of the folders containing the yaml
                                    files to be merged.
        definitions (str or dict, optional): name of the section containing string template
                                                definitions or a dictionary with the same
        filename (str, optional): the name of the file to be merged. If None, all the yaml
                                  files in the folders will be merged.
                                  If a string is passed, only the yaml file with
                                  the matching name will be merged.
        merged_dict (dict, optional): the dictionary to be updated
        loglevel (str, optional): the loglevel to be used

    Returns:
        A dictionary containing the merged contents of all the yaml files.
    """
    logger = log_configure(log_name='yaml', log_level=loglevel)

    if merged_dict is None:
        logger.debug('Creating a new dictionary')
        merged_dict = defaultdict(dict)
    else:
        logger.debug('Updating an existing dictionary')

    if isinstance(folder_path, str):
        folder_path = [folder_path]

    for folder in folder_path:
        if not os.path.exists(folder):
            raise ValueError(f'ERROR: {folder} not found: it is required to have this folder!')
        else:  # folder exists
            if filename is None:  # Merging all the existing yaml files in the folder
                for filename in os.listdir(folder):
                    if filename.endswith(('.yml', '.yaml')):
                        file_path = os.path.join(folder, filename)
                        yaml_dict = load_yaml(file_path, definitions)
                        for key, value in yaml_dict.items():
                            merged_dict[key].update(value)
            else:  # Merging a specific file
                file_path = os.path.join(folder, filename)
                yaml_dict = load_yaml(file_path, definitions)
                for key, value in yaml_dict.items():
                    merged_dict[key].update(value)

    logger.debug('Dictionary updated')
    logger.debug(f'Keys: {merged_dict.keys()}')

    return dict(merged_dict)
