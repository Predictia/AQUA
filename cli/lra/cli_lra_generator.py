#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
AQUA regridding tool to create low resolution archive.
Make use of aqua.LRA_Generator class to perform the regridding.
Functionality can be controlled through CLI options and
a configuration yaml file.
'''
import os
import sys
import argparse
from aqua import LRA_Generator
from aqua.util import load_yaml, get_arg

def parse_arguments(args):
    """
    Parse command line arguments
    """

    parser = argparse.ArgumentParser(description='AQUA LRA generator')
    parser.add_argument('-c', '--config', type=str, help='yaml configuration file')
    parser.add_argument('-f', '--fix', action="store_true", help='fix existing output')
    parser.add_argument('-w', '--workers', type=str, help='number of dask workers')
    parser.add_argument('-d', '--dry', action="store_true", help='dry run')
    parser.add_argument('-o', '--overwrite', action="store_true", help='overwrite existing output')
    parser.add_argument('-l', '--loglevel', type=str, help='log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) [default: INFO]')

    return parser.parse_args(args)

if __name__ == '__main__':
    """
    Main function
    """
    verbose = True
    args = parse_arguments(sys.argv[1:])
    loglevel = get_arg(args, 'loglevel', 'INFO')

    dry = get_arg(args, 'dry', False)
    overwrite = get_arg(args, 'overwrite', False)
    fix = get_arg(args, 'fix', False)

    workers = get_arg(args, 'workers', 1)

    file = get_arg(args, 'config', 'lra_config.yaml')
    print('Reading configuration yaml file..')

    config = load_yaml(file)

    resolution = config['target']['resolution']
    frequency = config['target']['frequency']
    outdir = config['target']['outdir']
    tmpdir = config['target']['tmpdir']

    for model in config['catalog'].keys():
        for exp in config['catalog'][model].keys():
            for source in config['catalog'][model][exp].keys():
                varlist = config['catalog'][model][exp][source]['vars']
                if verbose:
                    print(f'Processing {model}-{exp}-{source}...')
                    lra = LRA_Generator(model=model, exp=exp, source=source,var=varlist,
                                        resolution=resolution, frequency=frequency, fix=fix,
                                        outdir=outdir, tmpdir=tmpdir,nproc=workers,
                                        loglevel=loglevel, dry=dry, overwrite=overwrite)
                    lra.retrieve()
                    lra.generate_lra()
                if verbose:
                    print(f'Processed {source}...')
            if verbose:
                print(f'Processed {exp}...')
        if verbose:
            print(f'Processed {model}...')
    if verbose:
        print('Done.')