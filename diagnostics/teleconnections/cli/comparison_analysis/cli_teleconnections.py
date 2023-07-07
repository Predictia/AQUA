#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
AQUA teleconnections command line interface. Reads configuration file and
performs teleconnections diagnostic.
'''
import sys
import argparse

from aqua.util import load_yaml, get_arg
from teleconnections.plots import maps_plot
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
        # Build lists for comparison plots
        regs = []
        corrs = []
        models = []
        exps = []

        # Obs as first element
        regs.append(teleconnection_obs.regression)
        corrs.append(teleconnection_obs.correlation)
        models.append(teleconnection_obs.model)
        exps.append(teleconnection_obs.exp)

        if loglevel == 'DEBUG':
            print('Saving figures...')
        for teleconnection in teleconnections:
            teleconnection.plot_index()

            # Build lists for comparison plots
            regs.append(teleconnection.regression)
            corrs.append(teleconnection.correlation)
            models.append(teleconnection.model)
            exps.append(teleconnection.exp)

        teleconnection_obs.plot_index()

        # Comparison plots
        # 1. Regression
        title = telecname + ' regression maps'
        filename = 'teleconnections_all-models_' + teleconnection_obs.model + '_' + telecname + '_regression.pdf'
        if loglevel == 'DEBUG' or loglevel == 'INFO':
            print('Saving regression comparison plot: ' + filename)
        maps_plot(maps=regs, models=models, exps=exps, loglevel=loglevel, title=title,
                  filename=filename, save=True)

        # 2. Correlation
        title = telecname + ' correlation maps'
        if loglevel == 'DEBUG' or loglevel == 'INFO':
            print('Saving correlation comparison plot: ' + filename)
        filename = 'teleconnections_all-models_' + teleconnection_obs.model + '_' + telecname + '_correlation.pdf'
        maps_plot(maps=corrs, models=models, exps=exps, loglevel=loglevel, title=title,
                  filename=filename, save=True)

        # 3. Comparison with obs

        # 3.1 Create xarray
        reg_comp = []
        corr_comp = []
        for teleconnection in teleconnections:
            comp = teleconnection.regression - teleconnection_obs.regression
            reg_comp.append(comp)

            comp = teleconnection.correlation - teleconnection_obs.correlation
            corr_comp.append(comp)

        # 3.2 Plot
        title = telecname + ' regression maps comparison with ' + teleconnection_obs.model
        filename = 'teleconnections_all-models_' + teleconnection_obs.model + '_' + telecname + '_regression_diff.pdf'
        if loglevel == 'DEBUG' or loglevel == 'INFO':
            print('Saving regression difference plot: ' + filename)
        maps_plot(maps=reg_comp, models=models, exps=exps, loglevel=loglevel,
                  title=title, filename=filename, save=True)

        title = telecname + ' correlation maps comparison with ' + teleconnection_obs.model
        filename = 'teleconnections_all-models_' + teleconnection_obs.model + '_' + telecname + '_correlation_diff.pdf'
        if loglevel == 'DEBUG' or loglevel == 'INFO':
            print('Saving correlation difference plot: ' + filename)
        maps_plot(maps=corr_comp, models=models, exps=exps, loglevel=loglevel,
                  title=title, filename=filename, save=True)

    print('Teleconnections diagnostic test run completed.')
