#!/usr/bin/env python3

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
AQUA regridding tool demo to create low resolution archive
This tool implements regridding of required files from the intake catalog
using precomputed weights and sparse-array multiplication using smmregrid package 
included in AQUA. Functionality can be controlled through CLI options.
'''
import sys
sys.path.append("..")

import argparse
from aqua import Reader
from aqua.util import load_yaml
import dask
from dask.distributed import Client, LocalCluster
from time import time
import os
import logging
import yaml



def lra(modelname, expname, sourcename, resolution, frequency, varlist, outdir, dryrun=False):
    """
    Function to produce interpolation to disk of a selected variables
    """

    if dryrun:
        logging.info('IMPORTANT: no file will be created, this is a dry run')

    lowdir = os.path.join(outdir, f'{expname}-{resolution}-{frequency}')
    os.makedirs(lowdir, exist_ok=True)
    logging.info(f'Target directory is {lowdir}')

    logging.info(f'Accessing catalog for {modelname}-{expname}-{sourcename}...')
    reader = Reader(model=modelname, exp=expname, source=sourcename,
                    regrid=resolution, freq=frequency, configdir="../config") # this is hardcoded
    
    logging.info('Retrieving data...')
    data = reader.retrieve(fix=False)

    # option for time encoding, defined once for all
    time_encoding = {'units': 'days since 1970-01-01',
                 'calendar': 'standard',
                 'dtype': 'float64'}

    for var in varlist:
        tic = time()

        logging.info(f'Processing variable {var}...')
        averaged = reader.average(data[var]) # here level selection can be applied
        interp = reader.regrid(averaged) # here we can apply time selection, for instance if we want to process one year at the time
        logging.info(f'Output will have shape {interp.shape}')
        logging.info(f'From {min(interp.time.data)} to {max(interp.time.data)}')
        

        
        
        # we can of course extend this and also save to grib
        # if dryrun is true, not save, just check you have everything
        if not dryrun:
            logging.info(f'Writing it to disk...')
            outname = os.path.join(lowdir, f'{var}_{expname}.nc')
            interp.to_netcdf(outname, encoding={'time': time_encoding})

        toc = time()
        logging.info('Done in {:.4f} seconds'.format(toc - tic))


def parse_arguments(args):
    """Parse CLI arguments"""

    parser = argparse.ArgumentParser(description='AQUA regridder')
    parser.add_argument('-c', '--config', type=str, help='yaml configuration file')
    # parser.add_argument('-o', '--outdir', type=str, help='output directory')
    # parser.add_argument('-m', '--model', type=str, help='input model')
    # parser.add_argument('-e', '--exp', type=str, help='input experiment')
    # parser.add_argument('-s', '--source', type=str, help='input source')
    # parser.add_argument('-r', '--resolution', type=str, help='target resolution')
    parser.add_argument('-w', '--workers', type=str, help='number of dask workers')
    parser.add_argument('-d', '--dry', type=str, help='dry run, no file creation (default True)')
    # parser.add_argument('-f', '--frequency', type=str, help='output frequency for averaging')
    #parser.add_argument('-v', '--var', type=str, help='select variable')

    return parser.parse_args(args)

def get_arg(args, arg, default):
    """Aider function to get arguments"""

    res = getattr(args, arg)
    if not res:
        res = default
    return res

# setting up dask
if __name__ == "__main__":

    args = parse_arguments(sys.argv[1:])

    #assign from parsed
    # model = get_arg(args, 'model', None)
    # exp = get_arg(args, 'exp', None)
    # source = get_arg(args, 'source', None)
    # resolution = get_arg(args, 'resolution', 'r100')
    # outdir = get_arg(args, 'outdir', None)
    # frequency = get_arg(args, 'frequency', 'mon')
    workers = int(get_arg(args, 'workers', 1))
    dry = int(get_arg(args, 'dry', True))
    config = get_arg(args, 'config', 'config_lra.yml')

    # set default loglevel
    logging.basicConfig(level='INFO')

    # set up clusters if more than workers is provided
    if workers > 1: 
        cluster = LocalCluster(threads_per_worker=1, n_workers=workers)
        client = Client(cluster)
    else: 
        dask.config.set(scheduler="synchronous")

    cfg = load_yaml(config)
    resolution = cfg['target']['resolution']
    frequency = cfg['target']['frequency']
    outdir = cfg['target']['outdir']

    # loop on all the elements of the catalog
    for model in cfg['catalog'].keys():
        for exp in cfg['catalog'][model].keys():
            for sourceid in cfg['catalog'][model][exp].keys():
                varlist = cfg['catalog'][model][exp][sourceid]['vars']
                if varlist: 
                    # call the function
                    lra(modelname=model, expname=exp, sourcename=sourceid, resolution=resolution,
                        frequency=frequency, varlist=varlist, outdir=outdir, dryrun=dry)
    
    # shutdown the cluster
    if workers > 1:
        client.close()
    
    logging.info('Everything completed... goodbye!')
