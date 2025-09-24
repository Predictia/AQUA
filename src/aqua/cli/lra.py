#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
AQUA regridding tool to create low resolution archive.
Make use of aqua.LRA_Generator class to perform the regridding.
Functionality can be controlled through CLI options and
a configuration yaml file.
'''

import sys
import argparse
from aqua import LRAgenerator
from aqua.util import load_yaml, get_arg, to_list
from aqua import __version__ as version


def lra_parser(parser = None):
    """
    Parse command line arguments for the LRA CLI

    Args:
        Optional part to be extended with LRA options
    """

    if parser is None:
        parser = argparse.ArgumentParser(description='AQUA LRA generator')
    
    parser.add_argument('-c', '--config', type=str,
                        help='yaml configuration file')
    parser.add_argument('-f', '--fix', action="store_true",
                        help='fixer on existing data')
    parser.add_argument('-w', '--workers', type=str,
                        help='number of dask workers')
    parser.add_argument('-d', '--definitive', action="store_true",
                        help='definitive run with files creation')
    parser.add_argument('-o', '--overwrite', action="store_true",
                        help='overwrite existing output')
    parser.add_argument('-l', '--loglevel', type=str,
                        help='log level [default: WARNING]')
    parser.add_argument('--monitoring', action="store_true",
                        help='enable the dask performance monitoring. Will run a single chunk')
    parser.add_argument('--only-catalog', action="store_true",
                        help='To not run the LRA but simply create the catalog entries for netcdf and zarr')
    parser.add_argument('--catalog', type=str,
                        help='catalog to be processed. Use with coherence with --model, -exp and --source')
    parser.add_argument('-m', '--model', type=str,
                        help='model to be processed. Use with coherence with --exp and --source')
    parser.add_argument('-e', '--exp', type=str,
                        help='experiment to be processed. Use with coherence with --source and --model')
    parser.add_argument('-s', '--source', type=str,
                        help='source to be processed. Use with coherence with --exp and --var')
    parser.add_argument('-v', '--var', type=str,
                        help='var to be processed. Use with coherence with --source')
    parser.add_argument('--rebuild', action="store_true", help="Rebuild Reader areas and weights")
    parser.add_argument('--realization', type=str,
                        help='realization to be processed. Use with coherence with --model, --exp and --source')
    parser.add_argument('--stat', type=str,
                        help="statistic to be computed. Can be one of ['min', 'max', 'mean', 'std'].")
    parser.add_argument('--frequency', type=str,
                        help="Frequency of the LRA. Can be anything in the AQUA frequency.")
    parser.add_argument('--resolution', type=str,
                        help="Resolution of the LRA. Can be anything in the AQUA resolution.")

    #return parser.parse_args(arguments)
    return parser

def lra_execute(args):
    """
    Executing the LRA by parsing the arguments and configuring the machinery
    """

        # to check if GSV is available and return the version
    try:
        import gsv
        print('GSV version is: ' + gsv.__version__)
    except RuntimeError:
        print("GSV not available. FDB5 binary library not present on system.")
    except KeyError:
        print("GSV not available. Environment variables not correctly set.")

    print('AQUA version is: ' + version)

    file = get_arg(args, 'config', 'lra_config.yaml')
    print('Reading configuration yaml file..')

    # basic from configuration
    config = load_yaml(file)

    #safety check
    for item in ['target', 'paths', 'data', 'options']:
        if not item in config:
            raise KeyError(f'Configuration file {file} does not have the "{item}" key, please modify it according to the template')

    # main arguments
    resolution = config['target'].get('resolution')
    frequency = config['target'].get('frequency')
    region = config['target'].get('region', None)
    catalog = config['target'].get('catalog', None)
    stat = config['target'].get('stat', 'mean')
    
    # assig paths
    paths = config['paths']
    outdir = paths['outdir']
    tmpdir = paths['tmpdir']

    # options
    loglevel = config['options'].get('loglevel', 'WARNING')
    do_zarr = config['options'].get('zarr', False)
    verify_zarr = config['options'].get('verify_zarr', False)

    # command line override
    stat = get_arg(args, 'stat', stat)
    frequency = get_arg(args, 'frequency', frequency)
    resolution = get_arg(args, 'resolution', resolution)
    loglevel = get_arg(args, 'loglevel', loglevel)

    definitive = get_arg(args, 'definitive', False)
    monitoring = get_arg(args, 'monitoring', False)
    overwrite = get_arg(args, 'overwrite', False)
    rebuild = get_arg(args, 'rebuild', False)
    only_catalog = get_arg(args, 'only_catalog', False)
    if only_catalog:
        print('--only-catalog selected, doing a lot of noise but in the end producing only catalog update!')
    fix = get_arg(args, 'fix', True)
    default_workers = get_arg(args, 'workers', 1)
    

    lra_cli(args=args, config=config, catalog=catalog, resolution=resolution,
            frequency=frequency, fix=fix,
            outdir=outdir, tmpdir=tmpdir, loglevel=loglevel,
            region=region, stat=stat,
            definitive=definitive, overwrite=overwrite, rebuild=rebuild,
            default_workers=default_workers,
            monitoring=monitoring, do_zarr=do_zarr, verify_zarr=verify_zarr, only_catalog=only_catalog)

def lra_cli(args, config, catalog, resolution, frequency, fix, outdir, tmpdir, loglevel,
            region=None, stat='mean',
            definitive=False, overwrite=False,
            rebuild=False, monitoring=False,
            default_workers=1, do_zarr=False, verify_zarr=False,
            only_catalog=False):
    """
    Running the default LRA from CLI, looping on all the configuration model/exp/source/var combination
    Optional feature for each source can be defined as `zoom`, `workers` and `realizations`
    Options for dry run and overwriting, as well as monitoring and zarr creation, are available

    Args:
        args: argparse arguments
        config: configuration dictionary
        catalog: catalog to be processed
        resolution: resolution of the LRA
        frequency: frequency of the LRA
        fix: fixer option
        outdir: output directory
        tmpdir: temporary directory
        loglevel: log level
        region: region to be processed
        stat: statistic to be computed
        definitive: bool flag to create definitive files
        overwrite: bool flag to overwrite existing files
        rebuild: bool flag to rebuild the areas and weights
        default_workers: default number of workers
        monitoring: bool flag to enable the dask monitoring
        do_zarr: bool flag to create zarr
        verify_zarr: bool flag to verify zarr
        only_catalog: bool flag to only update the catalog
    """

    models = to_list(get_arg(args, 'model', config['data']))
    for model in models:
        exps = to_list(get_arg(args, 'exp', config['data'][model]))
        for exp in exps:

            # if you do require the entire catalog generator
            sources = to_list(get_arg(args, 'source', config['data'][model][exp]))
            for source in sources:
                # get info on potential realizations from the configuration file or from the args of command line
                realizations = get_arg(args, 'realization', config['data'][model][exp][source].get('realizations'))
                loop_realizations = to_list(realizations) if realizations is not None else [1]

                # get info on varlist and workers
                varnames = to_list(get_arg(args, 'var', config['data'][model][exp][source]['vars']))

                # get the number of workers for this specific configuration
                workers = config['data'][model][exp][source].get('workers', default_workers)

                # loop in realizations
                for realization in loop_realizations:

                    # define realization as extra args only if this is found in the configuration file
                    extra_args = {'realization': realization} if realizations else {}
                    print(varnames)
                    for varname in varnames:

                        # get the zoom level - this might need some tuning for extra kwargs
                        zoom = config['data'][model][exp][source].get('zoom', None)
                        if zoom is not None:
                            extra_args = {**extra_args, **{'zoom': zoom}}
                        
                        # disabling rebuild if we are not in the first realization and first varname
                        if varname != varnames[0] or realization != loop_realizations[0]:
                            rebuild = False
                        # init the LRA
                        lra = LRAgenerator(catalog=catalog, model=model, exp=exp, source=source,
                                        var=varname, resolution=resolution,
                                        frequency=frequency, fix=fix,
                                        outdir=outdir, tmpdir=tmpdir,
                                        nproc=workers, loglevel=loglevel,
                                        region=region, stat=stat,
                                        definitive=definitive, overwrite=overwrite,
                                        rebuild=rebuild,
                                        performance_reporting=monitoring,
                                        exclude_incomplete=True,
                                        **extra_args)


                        
                        if not only_catalog:
                            # check that your LRA is not already there (it will not work in streaming mode)
                            lra.check_integrity(varname)

                            # retrieve and generate
                            lra.retrieve()
                            lra.generate_lra()

            # create the catalog once the loop is over
            lra.create_catalog_entry()
            if do_zarr:
                lra.create_zarr_entry(verify=verify_zarr)

    print('CLI LRA run completed. Have yourself a tasty pint of beer!')

# if you want to execute the script from terminal without the aqua entry point
if __name__ == '__main__':

    args = lra_parser().parse_args(sys.argv[1:])
    lra_execute(args)
   
