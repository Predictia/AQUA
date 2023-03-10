import yaml
import os
import sys
import operator
import re

def load_yaml(infile):
    """Load generic yaml file"""

    try:
        with open(infile, 'r', encoding='utf-8') as file:
            cfg = yaml.load(file, Loader=yaml.FullLoader)
    except IOError:
        sys.exit(f'ERROR: {infile} not found: you need to have this configuration file!')
    return cfg


def get_catalog_file(configdir=None):
    """
    Return the path to the configdir and to the catalogfile catalog file, 
    searching in a list of pre-defined directories. If configdir is provided, search only in that directory.
    
    Args:
        configdir (str, optional): Where to search the catalog  and other config files

    Returns:
        configdir (str): the dir of the catalog file and other config files
        catalog_file (str): the path of the catalog file
    
    """

    # if the configdir path is provided
    if configdir:
        catalog_file = os.path.join(configdir, "catalog.yaml")
    else:
        # set of predefined folders to browse
        configdirs = ['./config', '../config', '../../config']
        homedir = os.environ.get('HOME')
        # if the home is defined
        if homedir:
            configdirs.append(os.path.join(homedir, '.aqua', 'config'))
        for configdir in configdirs:
            catalog_file = os.path.join(configdir, "catalog.yaml")
            if os.path.exists(catalog_file):
                break
    
    # safety check to verify existence of the catalogfile
    if os.path.exists(catalog_file):
        return configdir, catalog_file
    else:
        sys.exit('Cannot find the catalog file!')
        
    
# this is a tool to parse a CDO-based formula into mathematical operatos
# there might exists something more intelligent such as the pyparsing package
def _eval_formula(mystring, xdataset):
    """Evaluate the cmd string provided by the yaml file
    producing a parsing for the derived variables"""

    # Tokenize the original string
    token = [i for i in re.split('([^\\w.]+)', mystring) if i]
    if len(token) > 1:
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
            replacer = ops.get(p)(dct[token[x - 1]], dct[token[x + 1]])
            dct[name] = replacer
            token[x - 1] = name
            del token[x:x + 2]
    return replacer