"""YAML utility functions"""

import operator
import os
import re
import sys
import xarray as xr
from collections import defaultdict
from ruamel.yaml import YAML


def load_yaml(infile):
    """
    Load generic yaml file

    Args:
        infile(str): a file path

    Returns:
        A dictionary with the yaml file keys
    """
    yaml = YAML(typ='rt')  # default, if not specified, is 'rt' (round-trip)

    try:
        with open(infile, 'r', encoding='utf-8') as file:
            cfg = yaml.load(file)
    except IOError:
        sys.exit(f'ERROR: {infile} not found: you need to have this configuration file!')
    return cfg


def load_multi_yaml(folder_path):
    """
    Load and merge all yaml files located in a given folder
    into a single dictionary.

    Args:
        folder_path(str):   The path of the folder containing the yaml
                            files to be merged.

    Returns:
        A dictionary containing the merged contents of all the yaml files.
    """
    yaml = YAML()  # default, if not specified, is 'rt' (round-trip)

    merged_dict = defaultdict(dict)
    for filename in os.listdir(folder_path):
        if filename.endswith(('.yml', '.yaml')):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                yaml_dict = yaml.load(file)
                for key, value in yaml_dict.items():
                    merged_dict[key].update(value)
    return dict(merged_dict)


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
