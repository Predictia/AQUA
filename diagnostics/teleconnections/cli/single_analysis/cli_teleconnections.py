#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
AQUA teleconnections command line interface for a single dataset.
Reads configuration file and performs teleconnections diagnostic.
'''
import argparse
import sys

from aqua.util import load_yaml, get_arg
from teleconnections.plots import single_map_plot
from teleconnections.tc_class import Teleconnection
from teleconnections.tools import get_dataset_config

def parse_arguments(args):
    """Parse command line arguments"""

    parser = argparse.ArgumentParser(description='Teleconnections CLI')
    parser.add_argument('-c', '--config', type=str,
                        help='yaml configuration file')
    parser.add_argument('-d', '--definitive', action='store_true',
                        required=False,
                        help='if True, files are saved, default is True')
    parser.add_argument('-l', '--loglevel', type=str,
                        help='log level [default: WARNING]')

    # This arguments will override the configuration file if provided
    parser.add_argument('--model', type=str, help='model name',
                        required=False)
    parser.add_argument('--exp', type=str, help='experiment name',
                        required=False)
    parser.add_argument('--source', type=str, help='source name',
                        required=False)
    parser.add_argument('--outputdir', type=str, help='output directory',
                        required=False)

    return parser.parse_args(args)

if __name__ == '__main__':

    print('Running teleconnections diagnostic...')
    args = parse_arguments(sys.argv[1:])

    # Read configuration file
    file = get_arg(args, 'config', 'teleconnections_config.yaml')
    print('Reading configuration yaml file..')
    config = load_yaml(file)

    loglevel = get_arg(args, 'loglevel', 'WARNING')

    # Turning on/off the teleconnections
    # the try/except is used to avoid KeyError if the teleconnection is not
    # defined in the yaml file, since we have oceanic and atmospheric
    # configuration files
    try:
        NAO = config['teleconnections']['NAO']
    except KeyError:
        NAO = False

    try:
        ENSO = config['teleconnections']['ENSO']
    except KeyError:
        ENSO = False

    if NAO:
        print('Running NAO teleconnection...')

    if ENSO:
        print('Running ENSO teleconnection...')
