#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
AQUA teleconnections command line interface for a single dataset.
Reads configuration file and performs teleconnections diagnostic.
'''
import sys
import argparse

from aqua.util import load_yaml, get_arg
from teleconnections.tc_class import Teleconnection


def parse_arguments(args):
    """
    Parse command line arguments
    """

    parser = argparse.ArgumentParser(description='Teleconnections CLI')
    parser.add_argument('-c', '--config', type=str,
                        help='yaml configuration file')
    parser.add_argument('-d', '--definitive', type=bool,
                        help='if True, files are saved, default is False')
    parser.add_argument('-l', '--loglevel', type=str,
                        help='log level [default: WARNING]')

    return parser.parse_args(args)


def get_dataset_config(sources=None, dataset_source=None, config_dict=None):
    """
    Get configuration parameters for a given dataset_source

    Args:
        sources (dict): dictionary with configuration parameters
        dataset_source (str): dataset source name
        config_dict (dict, opt): dictionary to store configuration parameters

    Returns:
        config_dict (dict): dictionary with configuration parameters
                            of the individual dataset_source

    Raises:
        ValueError: if dataset_source or sources is None
    """

    if dataset_source is None:
        raise ValueError('dataset_source is None')

    if sources is None:
        raise ValueError('sources is None')

    if config_dict is None:
        config_dict = {}

    # Get configuration parameters
    # Search for entries under 'sources' key
    model = sources[dataset_source]['model']
    config_dict['model'] = model
    exp = sources[dataset_source]['exp']
    config_dict['exp'] = exp
    source = sources[dataset_source]['source']
    config_dict['source'] = source

    try:
        regrid = sources[dataset_source]['regrid']
        if regrid is False:
            regrid = None
    except KeyError:
        regrid = None
    config_dict['regrid'] = regrid

    try:
        freq = sources[dataset_source]['freq']
        if freq is False:
            freq = None
    except KeyError:
        freq = None
    config_dict['freq'] = freq

    try:
        zoom = sources[dataset_source]['zoom']
    except KeyError:
        zoom = None
    if zoom is not (None or False):
        config_dict['zoom'] = zoom

    try:
        months_window = sources[dataset_source]['months_window']
    except KeyError:
        months_window = 3
    config_dict['months_window'] = months_window

    try:
        outputfig = sources[dataset_source]['outputfig']
    except KeyError:
        outputfig = None
    config_dict['outputfig'] = outputfig

    try:
        outputdir = sources[dataset_source]['outputdir']
    except KeyError:
        outputdir = None
    config_dict['outputdir'] = outputdir

    try:
        filename = sources[dataset_source]['filename']
    except KeyError:
        filename = None
    config_dict['filename'] = filename

    return config_dict


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
    config_dict = get_dataset_config(sources=config,
                                     dataset_source='source')
    print(config_dict)

    teleconnection = Teleconnection(telecname=telecname, configdir=configdir,
                                    **config_dict,  # from cli config file
                                    savefig=savefig, savefile=savefile,
                                    loglevel=loglevel)

    teleconnection.retrieve()
    teleconnection.evaluate_index()
    teleconnection.evaluate_correlation()
    teleconnection.evaluate_regression()

    if savefig:
        teleconnection.plot_index()

    print('Teleconnections diagnostic test run completed.')
