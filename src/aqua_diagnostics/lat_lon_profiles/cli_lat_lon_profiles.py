#!/usr/bin/env python3
"""
Command-line interface for LatLonProfiles diagnostic.

This CLI allows to run the LatLonProfiles diagnostic for zonal or meridional profiles.
Details of the run are defined in a yaml configuration file for a
single or multiple experiments.
"""

import sys
import argparse
from aqua.logger import log_configure
from aqua.util import get_arg
from aqua.version import __version__ as aqua_version
from aqua.diagnostics.core import template_parse_arguments, open_cluster, close_cluster
from aqua.diagnostics.core import load_diagnostic_config, merge_config_args
from aqua.diagnostics.lat_lon_profiles import LatLonProfiles, PlotLatLonProfiles


def parse_arguments(args):
    """Parse command-line arguments for LatLonProfiles diagnostic.

    Args:
        args (list): list of command-line arguments to parse.
    """
    parser = argparse.ArgumentParser(description='LatLonProfiles CLI')
    parser = template_parse_arguments(parser)
    return parser.parse_args(args)


if __name__ == '__main__':
    args = parse_arguments(sys.argv[1:])

    loglevel = get_arg(args, 'loglevel', 'WARNING')
    logger = log_configure(log_level=loglevel, log_name='LatLonProfiles CLI')
    logger.info(f"Running LatLonProfiles diagnostic with AQUA version {aqua_version}")

    cluster = get_arg(args, 'cluster', None)
    nworkers = get_arg(args, 'nworkers', None)

    client, cluster, private_cluster = open_cluster(nworkers=nworkers, cluster=cluster, loglevel=loglevel)

    # Load the configuration file and then merge it with the command-line arguments,
    # overwriting the configuration file values with the command-line arguments.
    config_dict = load_diagnostic_config(diagnostic='lat_lon_profiles', config=args.config,
                                         default_config='config_lat_lon_profiles.yaml',
                                         loglevel=loglevel)
    config_dict = merge_config_args(config=config_dict, args=args, loglevel=loglevel)

    regrid = get_arg(args, 'regrid', None)
    logger.info(f"Regrid option is set to {regrid}")
    realization = get_arg(args, 'realization', None)
    # This reader_kwargs will be used if the dataset corresponding value is None or not present
    if realization:
        reader_kwargs = {'realization': realization}
    else:
        reader_kwargs = config_dict['datasets'][0].get('reader_kwargs') or {}

    # Output options
    outputdir = config_dict['output'].get('outputdir', './')
    rebuild = config_dict['output'].get('rebuild', True)
    save_pdf = config_dict['output'].get('save_pdf', True)
    save_png = config_dict['output'].get('save_png', True)
    dpi = config_dict['output'].get('dpi', 300)
    create_catalog_entry = config_dict['output'].get('create_catalog_entry', True)

    # LatLonProfiles diagnostic
    if 'lat_lon_profiles' in config_dict['diagnostics']:
        if config_dict['diagnostics']['lat_lon_profiles']['run']:
            logger.info("LatLonProfiles diagnostic is enabled.")

            diagnostic_name = config_dict['diagnostics']['lat_lon_profiles'].get('diagnostic_name', 'lat_lon_profiles')
            mean_type = config_dict['diagnostics']['lat_lon_profiles'].get('mean_type', 'zonal')
            center_time = config_dict['diagnostics']['lat_lon_profiles'].get('center_time', True)
            exclude_incomplete = config_dict['diagnostics']['lat_lon_profiles'].get('exclude_incomplete', True)
            box_brd = config_dict['diagnostics']['lat_lon_profiles'].get('box_brd', True)
            compute_std = config_dict['diagnostics']['lat_lon_profiles'].get('compute_std', False)
            
            # Frequency options
            freq = []
            if config_dict['diagnostics']['lat_lon_profiles'].get('seasonal', True):
                freq.append('seasonal')
            if config_dict['diagnostics']['lat_lon_profiles'].get('longterm', True):
                freq.append('longterm')

            for var in config_dict['diagnostics']['lat_lon_profiles'].get('variables', []):
                var_name = var.get('name')
                var_units = var.get('units', None)
                var_long_name = var.get('long_name', None)
                var_standard_name = var.get('standard_name', None)
                regions = var.get('regions', [None])  # None = global
                
                logger.info(f"Running LatLonProfiles diagnostic for variable {var_name} with mean_type={mean_type}")
                
                for region in regions:
                    try:
                        logger.info(f"Running LatLonProfiles diagnostic in region {region if region else 'global'}")

                        # Initialize a list of LatLonProfiles objects for each dataset
                        profiles = [None] * len(config_dict['datasets'])
                        
                        for i, dataset in enumerate(config_dict['datasets']):
                            logger.info(f'Processing dataset: {dataset}')
                            
                            init_args = {
                                'catalog': dataset['catalog'],
                                'model': dataset['model'],
                                'exp': dataset['exp'],
                                'source': dataset['source'],
                                'regrid': regrid if regrid is not None else dataset.get('regrid', None),
                                'startdate': dataset.get('startdate'),
                                'enddate': dataset.get('enddate'),
                                'region': region,
                                'mean_type': mean_type,
                                'diagnostic_name': diagnostic_name,
                                'loglevel': loglevel
                            }
                            
                            profiles[i] = LatLonProfiles(**init_args)
                            
                            run_args = {
                                'var': var_name,
                                'units': var_units,
                                'long_name': var_long_name,
                                'standard_name': var_standard_name,
                                'std': compute_std,
                                'freq': freq,
                                'exclude_incomplete': exclude_incomplete,
                                'center_time': center_time,
                                'box_brd': box_brd,
                                'outputdir': outputdir,
                                'rebuild': rebuild,
                                'reader_kwargs': dataset.get('reader_kwargs') or reader_kwargs
                            }
                            
                            profiles[i].run(**run_args)

                        # Process reference data if specified
                        profile_ref = None
                        if 'references' in config_dict and len(config_dict['references']) > 0:
                            ref_config = config_dict['references'][0]  # Usa il primo reference
                            logger.info(f"Processing reference data: {ref_config}")
                            
                            ref_init_args = {
                                'catalog': ref_config['catalog'],
                                'model': ref_config['model'],
                                'exp': ref_config['exp'],
                                'source': ref_config['source'],
                                'regrid': regrid if regrid is not None else ref_config.get('regrid', None),
                                'startdate': ref_config.get('std_startdate'),
                                'enddate': ref_config.get('std_enddate'),
                                'region': region,
                                'mean_type': mean_type,
                                'diagnostic_name': diagnostic_name,
                                'loglevel': loglevel
                            }
                            
                            profile_ref = LatLonProfiles(**ref_init_args)
                                                    
                            ref_run_args = {
                                'var': var_name,
                                'units': var_units,
                                'long_name': var_long_name,
                                'standard_name': var_standard_name,
                                'std': True,  # Always compute std for reference
                                'freq': freq,
                                'exclude_incomplete': exclude_incomplete,
                                'center_time': center_time,
                                'box_brd': box_brd,
                                'outputdir': outputdir,
                                'rebuild': rebuild,
                                'reader_kwargs': ref_config.get('reader_kwargs') or {}
                            }
                            
                            profile_ref.run(**ref_run_args)

                        # Plot the profiles
                        if save_pdf or save_png:
                            logger.info(f"Plotting LatLonProfiles diagnostic for {var_name}")
                            
                            # Plot longterm (annual mean) if enabled
                            if 'longterm' in freq:
                                logger.info("Creating longterm (annual) plot")
                                
                                longterm_data = [profiles[i].longterm for i in range(len(profiles))]
                                
                                plot_args = {
                                    'data': longterm_data,
                                    'ref_data': profile_ref.longterm if profile_ref else None,
                                    'ref_std_data': profile_ref.std_annual if profile_ref else None,
                                    'data_type': 'longterm',
                                    'loglevel': loglevel
                                }
                                
                                plot_longterm = PlotLatLonProfiles(**plot_args)
                                
                                if save_pdf:
                                    plot_longterm.run(outputdir=outputdir, rebuild=rebuild, 
                                                     dpi=dpi, format='pdf', style=None)
                                if save_png:
                                    plot_longterm.run(outputdir=outputdir, rebuild=rebuild, 
                                                     dpi=dpi, format='png', style=None)

                            # Plot seasonal (4-panel) if enabled
                            if 'seasonal' in freq:
                                logger.info("Creating seasonal (4-panel) plot")
                                
                                # Prepare seasonal data for all 4 seasons
                                combined_seasonal_data = []
                                combined_ref_data = []
                                combined_ref_std_data = []
                                
                                for season_idx in range(4):  # DJF, MAM, JJA, SON
                                    season_data = [profiles[i].seasonal[season_idx] for i in range(len(profiles))]
                                    combined_seasonal_data.append(season_data)
                                    
                                    if profile_ref:
                                        combined_ref_data.append(profile_ref.seasonal[season_idx])
                                        combined_ref_std_data.append(profile_ref.std_seasonal[season_idx])
                                
                                plot_args = {
                                    'data': combined_seasonal_data,
                                    'ref_data': combined_ref_data if profile_ref else None,
                                    'ref_std_data': combined_ref_std_data if profile_ref else None,
                                    'data_type': 'seasonal',
                                    'loglevel': loglevel
                                }
                                
                                plot_seasonal = PlotLatLonProfiles(**plot_args)
                                
                                if save_pdf:
                                    plot_seasonal.run(outputdir=outputdir, rebuild=rebuild, 
                                                     dpi=dpi, format='pdf', style=None)
                                if save_png:
                                    plot_seasonal.run(outputdir=outputdir, rebuild=rebuild, 
                                                     dpi=dpi, format='png', style=None)

                    except Exception as e:
                        logger.error(f"Error running LatLonProfiles diagnostic for variable {var_name} in region {region if region else 'global'}: {e}")

    close_cluster(client=client, cluster=cluster, private_cluster=private_cluster, loglevel=loglevel)

    logger.info("LatLonProfiles diagnostic completed.")