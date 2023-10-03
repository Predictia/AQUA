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
from aqua.exceptions import NoDataError, NotEnoughDataError
from teleconnections.plots import single_map_plot
from teleconnections.tc_class import Teleconnection


def parse_arguments(args):
    """Parse command line arguments"""

    parser = argparse.ArgumentParser(description='Teleconnections CLI')

    parser.add_argument('-c', '--config', type=str,
                        help='yaml configuration file')
    parser.add_argument('-d', '--dry', action='store_true',
                        required=False,
                        help='if True, run is dry, no files are written')
    parser.add_argument('-l', '--loglevel', type=str,
                        help='log level [default: WARNING]')
    parser.add_argument('--obs', action='store_true',
                        required=False,
                        help='evaluate observations')

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

    # if obs we're performing the analysis for observations as well
    obs = get_arg(args, 'obs', False)

    dry = get_arg(args, 'dry', False)
    if dry:
        print('Dry run, no files will be written')
        savefig = False
        savefile = False
    else:
        savefig = True
        savefile = True

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
        try:
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
        except NoDataError:
            print('No data available for NAO teleconnection')
            sys.exit(0)

        # Data are available, are there enough?
        try:
            teleconnection.evaluate_index()
            teleconnection.evaluate_correlation()
            teleconnection.evaluate_regression()
        except NotEnoughDataError:
            print('Not enough data available for NAO teleconnection')
            sys.exit(0)

        if savefig:
            try:
                teleconnection.plot_index()
            except Exception as e:
                print('Error plotting NAO index: ', e)

            # Regression map
            try:
                single_map_plot(map=teleconnection.regression, loglevel=loglevel,
                                model=model, exp=exp,
                                outputdir=teleconnection.outputfig,
                                filename=teleconnection.filename + '_regression.pdf',
                                save=True, cbar_label='msl [hPa]', sym=True)
            except Exception as e:
                print('Error plotting NAO regression: ', e)

            # Correlation map
            try:
                single_map_plot(map=teleconnection.correlation, loglevel=loglevel,
                                model=model, exp=exp,
                                outputdir=teleconnection.outputfig,
                                filename=teleconnection.filename + '_correlation.pdf',
                                save=True, cbar_label='Pearson correlation', sym=True)
            except Exception as e:
                print('Error plotting NAO correlation: ', e)

        if obs:
            print('Analysing ERA5')
            try:
                teleconnection_ERA5 = Teleconnection(telecname='NAO', configdir=configdir,
                                                     regrid='r100',
                                                     model='ERA5', exp='era5', source='monthly',
                                                     months_window=months_window,
                                                     outputdir=os.path.join(outputnetcdf,
                                                                            'NAO'),
                                                    outputfig=os.path.join(outputpdf,
                                                                           'NAO'),
                                                     savefig=savefig, savefile=savefile,
                                                     loglevel=loglevel)
            except NoDataError:
                print('No ERA5 data available for NAO teleconnection')
                sys.exit(0)

            # Data are available, are there enough?
            try:
                teleconnection_ERA5.evaluate_index()
                teleconnection_ERA5.evaluate_correlation()
                teleconnection_ERA5.evaluate_regression()
            except NotEnoughDataError:
                print('Not enough data available for ERA5 NAO teleconnection')
                sys.exit(0)

            if savefig:
                try:
                    teleconnection_ERA5.plot_index()
                except Exception as e:
                    print('Error plotting ERA5 NAO index: ', e)

                # Regression map
                try:
                    single_map_plot(map=teleconnection_ERA5.regression, loglevel=loglevel,
                                    title='ERA5',
                                    outputdir=teleconnection_ERA5.outputfig,
                                    filename=teleconnection_ERA5.filename + '_regression.pdf',
                                    save=True, cbar_label='msl [hPa]', sym=True)
                except Exception as e:
                    print('Error plotting ERA5 NAO regression: ', e)

                # Correlation map
                try:
                    single_map_plot(map=teleconnection_ERA5.correlation, loglevel=loglevel,
                                    title='ERA5',
                                    outputdir=teleconnection_ERA5.outputfig,
                                    filename=teleconnection_ERA5.filename + '_correlation.pdf',
                                    save=True, cbar_label='Pearson correlation', sym=True)
                except Exception as e:
                    print('Error plotting ERA5 NAO correlation: ', e)

    if ENSO:
        print('Running ENSO teleconnection...')

        months_window = config['ENSO']['months_window']

        try:
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
        except NoDataError:
            print('No data available for ENSO teleconnection')
            sys.exit(0)

        # Data are available, are there enough?
        try:
            teleconnection.evaluate_index()
            teleconnection.evaluate_correlation()
            teleconnection.evaluate_regression()
        except NotEnoughDataError:
            print('Not enough data available for ENSO teleconnection')
            sys.exit(0)

        if savefig:
            try:
                teleconnection.plot_index()
            except Exception as e:
                print('Error plotting ENSO index: ', e)

            # Regression map
            try:
                single_map_plot(map=teleconnection.regression, loglevel=loglevel,
                                model=model, exp=exp,
                                outputdir=teleconnection.outputfig,
                                filename=teleconnection.filename + '_regression.pdf',
                                save=True, cbar_label='sst [K]', sym=True,
                                transform_first=True)
            except Exception as e:
                print('Error plotting ENSO regression: ', e)

            # Correlation map
            try:
                single_map_plot(map=teleconnection.correlation, loglevel=loglevel,
                                model=model, exp=exp,
                                outputdir=teleconnection.outputfig,
                                filename=teleconnection.filename + '_correlation.pdf',
                                save=True, cbar_label='Pearson correlation', sym=True,
                                transform_first=True)
            except Exception as e:
                print('Error plotting ENSO correlation: ', e)

        if obs:
            print('Analysing ERA5')

            try:
                teleconnection_ERA5 = Teleconnection(telecname='ENSO', configdir=configdir,
                                                     regrid='r100',
                                                     model='ERA5', exp='era5', source='monthly',
                                                     months_window=months_window,
                                                     outputdir=os.path.join(outputnetcdf,
                                                                            'ENSO'),
                                                     outputfig=os.path.join(outputpdf,
                                                                            'ENSO'),
                                                     savefig=savefig, savefile=savefile,
                                                     loglevel=loglevel)
            except NoDataError:
                print('No ERA5 data available for ENSO teleconnection')
                sys.exit(0)

            # Data are available, are there enough?
            try:
                teleconnection_ERA5.evaluate_index()
                teleconnection_ERA5.evaluate_correlation()
                teleconnection_ERA5.evaluate_regression()
            except NotEnoughDataError:
                print('Not enough data available for ERA5 ENSO teleconnection')
                sys.exit(0)

            if savefig:
                try:
                    teleconnection_ERA5.plot_index()
                except Exception as e:
                    print('Error plotting ERA5 ENSO index: ', e)

                # Regression map
                try:
                    single_map_plot(map=teleconnection_ERA5.regression, loglevel=loglevel,
                                    title='ERA5',
                                    outputdir=teleconnection_ERA5.outputfig,
                                    filename=teleconnection_ERA5.filename + '_regression.pdf',
                                    save=True, cbar_label='sst [K]', sym=True,
                                    transform_first=True)
                except Exception as e:
                    print('Error plotting ERA5 ENSO regression: ', e)

                # Correlation map
                try:
                    single_map_plot(map=teleconnection_ERA5.correlation, loglevel=loglevel,
                                    title='ERA5',
                                    outputdir=teleconnection_ERA5.outputfig,
                                    filename=teleconnection_ERA5.filename + '_correlation.pdf',
                                    save=True, cbar_label='Pearson correlation', sym=True,
                                    transform_first=True)
                except Exception as e:
                    print('Error plotting ERA5 ENSO correlation: ', e)

    print('Teleconnections diagnostic finished.')
