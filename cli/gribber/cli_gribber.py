#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AQUA command line tool to create .json files and
update the catalog yaml files with new entry
from the desired .grib file.
"""

import argparse
import os
import sys
from aqua.gribber import Gribber
from aqua.util import load_yaml, get_arg

def parse_arguments(args):
    """
    Parse command line arguments
    """

    parser = argparse.ArgumentParser(description='AQUA gribber')
    parser.add_argument('-c', '--config', type=str, required=False, 
                        help='yaml file with the directories')
    parser.add_argument('-m', '--model', type=str, required=False, 
                        help='Model name')
    parser.add_argument('-e', '--exp', type=str, required=False, 
                        help='Experiment name')
    parser.add_argument('-s', '--source', type=str, required=False, 
                        help='Source name')
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

    file = get_arg(args, 'config', None)

    # Get arguments
    if file:
        print('Reading yaml file')
        dir_file = load_yaml(file)
    
    model = get_arg(args, 'model', 'IFS')
    exp = get_arg(args, 'exp', 'tco1279-orca025')
    source = get_arg(args, 'source', 'ICMGG_atm2d')
    nprocs = get_arg(args, 'nprocs', 1)
    verbose = get_arg(args, 'verbose', False)
    replace = get_arg(args, 'replace', False)

    # Create Gribber object
    gribber = Gribber(model=model, exp=exp, source=source, nprocs=nprocs,
                        dir=dir_file,
                        verbose=verbose, replace=replace)
    
    # Create .catalog entry
    gribber.create_entry()