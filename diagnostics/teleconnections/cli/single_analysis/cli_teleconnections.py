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

    return parser.parse_args(args)

if __name__ == '__main__':

    print('Running teleconnections diagnostic...')
    args = parse_arguments(sys.argv[1:])

    # Read configuration file
    file = get_arg(args, 'config', 'teleconnections_config.yaml')
    print('Reading configuration yaml file..')
    config = load_yaml(file)

    loglevel = get_arg(args, 'loglevel', 'WARNING')

    NAO = config['teleconnections']['NAO']
    ENSO = config['teleconnections']['ENSO']

    if NAO:
        print('Running NAO teleconnection...')

    if ENSO:
        print('Running ENSO teleconnection...')
