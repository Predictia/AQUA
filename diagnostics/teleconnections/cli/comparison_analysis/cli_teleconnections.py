#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
AQUA teleconnections command line interface. Reads configuration file and
performs teleconnections diagnostic.
'''
import sys
import argparse

from aqua.util import load_yaml, get_arg
from teleconnections.tc_class import Teleconnection
from teleconnections.tools import get_dataset_config


def parse_arguments(args):
    """
    Parse command line arguments
    """

    parser = argparse.ArgumentParser(description='Teleconnections comparison CLI')
    parser.add_argument('-c', '--config', type=str,
                        required=False,
                        help='yaml configuration file')
    parser.add_argument('-d', '--definitive', action='store_true',
                        required=False,
                        help='if True, files are saved, default is False')
    parser.add_argument('-l', '--loglevel', type=str,
                        required=False,
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
    telecname = config['telecname']

    savefig = get_arg(args, 'definitive', False)
    savefile = get_arg(args, 'definitive', False)

    try:
        configdir = config['configdir']
    except KeyError:
        configdir = None

    # Get dataset configuration parameters
    # Search for entries under 'sources' key
    sources = config['sources']

    config_dict = []

    for dataset_source in sources:
        if loglevel == 'DEBUG':
            print('Obtaining config for dataset_source: ', dataset_source)

        config_dict.append(get_dataset_config(sources=sources,
                                              dataset_source=dataset_source))

    # Get observational dataset configuration parameters
    # Search for entries under 'obs' key
    obs_dict = config['obs']

    teleconnections = []

    # Initialize Teleconnection class
    for config in config_dict:
        if loglevel == 'DEBUG':
            print('Initializing Teleconnection class for dataset_source: ',
                  config['model'], config['exp'], config['source'])
        teleconnections.append(Teleconnection(telecname=telecname, **config,
                                              savefig=savefig,
                                              savefile=savefile,
                                              configdir=configdir,
                                              loglevel=loglevel))

    # Retrieve data, evaluate teleconnection index, correlation and regression
    for teleconnection in teleconnections:
        if loglevel == 'DEBUG':
            print('Retrieving data for dataset_source: ',
                  teleconnection.model, teleconnection.exp,
                  teleconnection.source)
        teleconnection.retrieve()
        teleconnection.evaluate_index()
        teleconnection.evaluate_correlation()
        teleconnection.evaluate_regression()

    # Initialize Teleconnection class for observational dataset
    teleconnection_obs = Teleconnection(telecname=telecname, **obs_dict,
                                        savefig=savefig, savefile=savefile,
                                        configdir=configdir, loglevel=loglevel)
    teleconnection_obs.retrieve()
    teleconnection_obs.evaluate_index()
    teleconnection_obs.evaluate_correlation()
    teleconnection_obs.evaluate_regression()

    if savefig:
        if loglevel == 'DEBUG':
            print('Saving figures...')
        for teleconnection in teleconnections:
            teleconnection.plot_index()

        teleconnection_obs.plot_index()

    print('Teleconnections diagnostic test run completed.')
