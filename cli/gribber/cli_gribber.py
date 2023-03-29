#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AQUA command line tool to create .json files and
update the catalog yaml files with new entry
from the desired .grib file.
"""

import argparse
import sys
from aqua.gribber import Gribber
from aqua.util import load_yaml, get_arg

def parse_arguments(args):
    """
    Parse command line arguments
    """

    parser = argparse.ArgumentParser(description='AQUA gribber')
    parser.add_argument('-c', '--config', type=str, required=False, 
                        help='yaml file with exp information and directories')
    parser.add_argument('-n', '--nprocs', type=int, required=False, 
                        help='Number of processors')
    parser.add_argument('-v', '--verbose', action='store_true', required=False, 
                        help='Verbose mode')
    parser.add_argument('-r', '--replace', action='store_true', required=False, 
                        help='Replace JSON file and indices if they exist')
    
    return parser.parse_args(args)

if __name__ == '__main__':
    """
    Main function
    """

    args = parse_arguments(sys.argv[1:])
    verbose = get_arg(args, 'verbose', True)

    file = get_arg(args, 'config', 'gribber_config.yaml')
    if verbose:
        print('Reading configuration yaml file..')
    
    config = load_yaml(file)
    
    model = config['id']['model']
    exp = config['id']['exp']
    source = config['id']['source']
    nprocs = get_arg(args, 'nprocs', 1)
    verbose = get_arg(args, 'verbose', False)
    replace = get_arg(args, 'replace', False)

    # Create Gribber object
    gribber = Gribber(model=model, exp=exp, source=source, nprocs=nprocs,
                        dir=config['dir'],
                        verbose=verbose, replace=replace)
    
    # Create .catalog entry
    gribber.create_entry()