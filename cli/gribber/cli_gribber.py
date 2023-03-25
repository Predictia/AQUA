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
from aqua.util import load_yaml

def parse_arguments(args):
    """
    Parse command line arguments
    """

    parser = argparse.ArgumentParser(description='AQUA gribber')
    parser.add_argument('-f', '--file', type=str, required=False, 
                        help='yaml file with the directories')
    parser.add_argument('-d', '--datadir', type=str, required=False,
                        help='Directory containing the .grib files')
    parser.add_argument('-t', '--tmpdir', type=str, required=False,
                        help='Directory where to store the temporary files')
    parser.add_argument('-j', '--jsondir', type=str, required=False,
                        help='Directory where to store the .json files')
    parser.add_argument('-c', '--catalogdir', type=str, required=False,
                        help='Directory where to store the catalog yaml files')
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

def get_arg(args, arg, default):
    """
    Support function to get arguments
    """

    res = getattr(args, arg)
    if not res:
        res = default
    return res

if __name__ == '__main__':
    """
    Main function
    """

    args = parse_arguments(sys.argv[1:])

    file = get_arg(args, 'file', None)

    # Get arguments
    if file:
        print('Reading yaml file')
        yamlfile = get_arg(args, 'file', None)
        dir_file = load_yaml(yamlfile)
        datadir = dir_file['datadir']
        tmpdir = dir_file['tmpdir']
        jsondir = dir_file['jsondir']
        catalogdir = dir_file['catalogdir']
    else:
        print('Reading command line arguments')
        datadir = get_arg(args, 'datadir', 
                          '/scratch/b/b382289/tco1279-orca025/nemo_deep/ICMGGc2')
        tmpdir = get_arg(args, 'tmpdir', 
                         '/scratch/b/b382289/gribscan')
        jsondir = get_arg(args, 'jsondir', 
                          '/work/bb1153/b382289/gribscan-json')
        catalogdir = get_arg(args, 'catalogdir', 
                             '/work/bb1153/b382289/AQUA/config/levante/catalog')
    
    model = get_arg(args, 'model', 'IFS')
    exp = get_arg(args, 'exp', 'tco1279-orca025')
    source = get_arg(args, 'source', 'ICMGG_atm2d')
    nprocs = get_arg(args, 'nprocs', 4)
    verbose = get_arg(args, 'verbose', False)
    replace = get_arg(args, 'replace', False)

    # Create Gribber object
    gribber = Gribber(model=model, exp=exp, source=source, nprocs=nprocs,
                        dir={'datadir': datadir, 'tmpdir': tmpdir,
                             'jsondir': jsondir, 'catalogdir': catalogdir},
                        verbose=verbose, replace=replace)
    
    # Create .catalog entry
    gribber.create_entry()