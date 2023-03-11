import yaml
import os
import sys
import operator
import re

def load_yaml(infile):
    """
    Load generic yaml file
    
    Args:
        infile(str): a file path

    Returns:
        A dictionary with the yaml file keys
    """

    try:
        with open(infile, 'r', encoding='utf-8') as file:
            cfg = yaml.load(file, Loader=yaml.FullLoader)
    except IOError:
        sys.exit(f'ERROR: {infile} not found: you need to have this configuration file!')
    return cfg


def get_config_dir(): 
    """
    Return the path to the configuration directory, 
    searching in a list of pre-defined directories.
    
     Args:
        None
     Returns:
         configdir (str): the dir of the catalog file and other config files
    """

    # set of predefined folders to browse
    configdirs = ['./config', '../config', '../../config']
    homedir = os.environ.get('HOME')

    # if the home is defined
    if homedir:
        configdirs.append(os.path.join(homedir, '.aqua', 'config'))
    for configdir in configdirs:
        if os.path.exists(os.path.join(configdir, "config.yaml")):
            break
    return configdir


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


def get_machine(configdir): 

    """
    Extract the name of the machine from the configuration file
    
    Args:
        configdir(str): the configuration file directory
     Returns:
        The name of the machine read from the configuration file
    """

    basefile = os.path.join(configdir, "config.yaml")
    if os.path.exists(basefile):
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

    basefile = os.path.join(configdir, "config.yaml")
    if os.path.exists(basefile):
        base = load_yaml(os.path.join(configdir, "config.yaml"))
        catalog_file = base['reader']['catalog'].format(machine=machine)
        if not os.path.exists(catalog_file):
            sys.exit(f'Cannot find catalog file in {catalog_file}')
        regrid_file = base['reader']['regrid'].format(machine=machine)
        if not os.path.exists(regrid_file):
            sys.exit(f'Cannot find catalog file in {regrid_file}')
        fixer_file = base['reader']['fixer'].format(machine=machine)
        if not os.path.exists(fixer_file):
            sys.exit(f'Cannot find catalog file in {fixer_file}')

    return catalog_file, regrid_file, fixer_file
