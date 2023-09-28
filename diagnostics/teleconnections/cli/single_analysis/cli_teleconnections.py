#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
AQUA teleconnections command line interface for a single dataset.
Reads configuration file and performs teleconnections diagnostic.
'''
import argparse
import os
import sys

from aqua.util import load_yaml, get_arg
from teleconnections.plots import single_map_plot
from teleconnections.tc_class import Teleconnection


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

    model = get_arg(args, 'model', config['model'])
    exp = get_arg(args, 'exp', config['exp'])
    source = get_arg(args, 'source', config['source'])

    savefig = get_arg(args, 'definitive', True)
    savefile = get_arg(args, 'definitive', True)

    # These may be needed if we're not using an LRA entry
    regrid = config['regrid']
    freq = config['freq']
    zoom = config['zoom']

    try:
        outputdir = get_arg(args, 'outputdir', config['outputdir'])
        outputnetcdf = os.path.join(outputdir, 'NetCDF')
        outputpdf = os.path.join(outputdir, 'pdf')
    except KeyError:
        outputdir = None
        outputnetcdf = None
        outputpdf = None

    configdir = config['configdir']

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

    # Executing the teleconnections
    if NAO:
        print('Running NAO teleconnection...')

        months_window = config['NAO']['months_window']

        teleconnection = Teleconnection(telecname='NAO', configdir=configdir,
                                        regrid=regrid, freq=freq, zoom=zoom,
                                        model=model, exp=exp, source=source,
                                        months_window=months_window,
                                        outputdir=os.path.join(outputnetcdf,
                                                               'NAO'),
                                        outputfig=os.path.join(outputpdf,
                                                               'NAO'),
                                        savefig=savefig, savefile=savefile,
                                        loglevel=loglevel)
        teleconnection.retrieve()
        teleconnection.evaluate_index()
        teleconnection.evaluate_correlation()
        teleconnection.evaluate_regression()

        if savefig:
            teleconnection.plot_index()
            # Regression map
            single_map_plot(map=teleconnection.regression, loglevel=loglevel,
                            outputdir=teleconnection.outputfig,
                            filename=teleconnection.filename + '_regression.pdf',
                            save=True, cbar_label=teleconnection.var, sym=True)
            # Correlation map
            single_map_plot(map=teleconnection.correlation, loglevel=loglevel,
                            outputdir=teleconnection.outputfig,
                            filename=teleconnection.filename + '_correlation.pdf',
                            save=True, cbar_label='Pearson correlation', sym=True)

    if ENSO:
        print('Running ENSO teleconnection...')

        months_window = config['ENSO']['months_window']

        teleconnection = Teleconnection(telecname='ENSO', configdir=configdir,
                                        regrid=regrid, freq=freq, zoom=zoom,
                                        model=model, exp=exp, source=source,
                                        months_window=months_window,
                                        outputdir=os.path.join(outputnetcdf,
                                                               'ENSO'),
                                        outputfig=os.path.join(outputpdf,
                                                               'ENSO'),
                                        savefig=savefig, savefile=savefile,
                                        loglevel=loglevel)
        teleconnection.retrieve()
        teleconnection.evaluate_index()
        teleconnection.evaluate_correlation()
        teleconnection.evaluate_regression()

        if savefig:
            teleconnection.plot_index()
            # Regression map
            single_map_plot(map=teleconnection.regression, loglevel=loglevel,
                            outputdir=teleconnection.outputfig,
                            filename=teleconnection.filename + '_regression.pdf',
                            save=True, cbar_label=teleconnection.var, sym=True)
            # Correlation map
            single_map_plot(map=teleconnection.correlation, loglevel=loglevel,
                            outputdir=teleconnection.outputfig,
                            filename=teleconnection.filename + '_correlation.pdf',
                            save=True, cbar_label='Pearson correlation', sym=True)
