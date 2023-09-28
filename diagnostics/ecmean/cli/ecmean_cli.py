#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
AQUA dummy diagnositc command line interface. Reads configuration file and performs dummy 
diagnostic
'''
import sys
import argparse
import xarray as xr
from ecmean.performance_indices import performance_indices
from aqua.util import load_yaml, get_arg
from aqua import Reader
from aqua.logger import log_configure


def parse_arguments(args):
    """
    Parse command line arguments
    """

    parser = argparse.ArgumentParser(description='ECmean Performance Indices  CLI')
    parser.add_argument('-c', '--config', type=str,
                        help='ecmean yaml configuration file', default='config_ecmean_cli.yaml')
    parser.add_argument('-m', '--model_atm', type=str,
                        help='atmospheric model to be analysed')
    parser.add_argument('-x', '--model_oce', type=str,
                        help='oceanic model to be analysed')
    parser.add_argument('-e', '--exp', type=str,
                        help='exp to be analysed')
    parser.add_argument('-s', '--source', type=str,
                        help='source to be analysed', default='lra-r100-monthly')
    parser.add_argument('-o', '--outputdir', type=str,
                        help='source to be analysed')
    parser.add_argument('-l', '--loglevel', type=str,
                        help='log level [default: WARNING]', default='warning')

    return parser.parse_args(args)

def reader_data(model, exp, source, keep_vars):
    """
    Simple function to retrieve and do some operation on reader data
    """
    # if False/None return empty array
    if not model:
        return None
    reader = Reader(model=model, exp=exp, source=source, areas=False, fix=False)
    data = reader.retrieve()

    # return only vars that are available
    if keep_vars is None:
        return data
    return data[[value for value in keep_vars if value in data.data_vars]]
 
if __name__ == '__main__':

    

    print('Running AQUA Performance Indices diagnostic...')
    args = parse_arguments(sys.argv[1:])
    file = get_arg(args, 'config', 'config_ecmean_cli.yaml')
   
    configfile = load_yaml(file)

    # setting default from configuration files
    model_atm = configfile['dataset']['model_atm']
    model_oce = configfile['dataset']['model_oce']
    exp = configfile['dataset']['exp']
    atm_vars = configfile['dataset']['atm_vars']
    oce_vars = configfile['dataset']['oce_vars']
    #year1 = configfile['dataset']['year1']
    #year2 = configfile['dataset']['year2']
    numproc = configfile['compute']['numproc']
    interface = configfile['setup']['interface_file']
    loglevel = configfile['setup']['loglevel']
    config = configfile['setup']['config_file']
    outputdir = configfile['setup']['outputdir']

    # activate override from command line
    loglevel = get_arg(args, 'loglevel', loglevel)
    exp = get_arg(args, 'exp', exp)
    source = get_arg(args, 'source', 'lra-r100-monthly')
    model_atm = get_arg(args, 'model_atm', model_atm)
    model_oce = get_arg(args, 'model_oce', model_oce)
    outputdir = get_arg(args, 'outputdir', outputdir)

    logger = log_configure(log_level=loglevel, log_name='PI')

    # load the data
    logger.warning('Loading atmospheric data %s', model_atm)
    data_atm = reader_data(model=model_atm, exp=exp, source=source, keep_vars=atm_vars)
    logger.warning('Loading oceanic data from %s', model_oce)
    data_oce = reader_data(model=model_oce, exp=exp, source=source, keep_vars=oce_vars)

    # there are issues with vertical axis in LRA
    #if 'level' in data_atm.coords:
    #    data_atm = data_atm.rename({'level': 'plev'})

    # create a single dataset
    if data_oce is None:
        data = data_atm
    elif data_atm is None:
        data = data_oce
    else:
        data = xr.merge([data_atm, data_oce])

    # guessing years from the dataset
    year1 = int(data.time[0].values.astype('datetime64[Y]').astype(str))
    year2 = int(data.time[-1].values.astype('datetime64[Y]').astype(str))
    logger.warning('Guessing starting year %s and ending year %s', year1, year2)


    # run the performance indices if you have at least 12 month of data
    if len(data.time)<12:
        logger.error('Not enough data, exiting...')
        exit(0)
    else: 
        logger.warning('Launching ECmean performance indices...')
        performance_indices(exp, year1, year2, numproc = numproc, config = config,
                interface = interface, loglevel = loglevel, outputdir = outputdir, 
                xdataset = data)


    print('AQUA ECmean4 Performance diagnostic run completed. Go outside and live your life!')
