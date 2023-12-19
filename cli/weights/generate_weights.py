#!/usr/bin/env python3
"""Loop on multiple datasets to create weights using the Reader"""

import sys
import argparse
from aqua import Reader, inspect_catalogue
from aqua.logger import log_configure
from aqua.util import load_yaml, get_arg


def parse_arguments(args):
    """Parse command line arguments"""

    parser = argparse.ArgumentParser(description='Weights Generator CLI')
    parser.add_argument('--config', type=str, 
                        help='path to configuration yaml file', default='config/weights_config.yml')
    # This arguments will override the configuration file if provided
    parser.add_argument('--catalogue', type=str,
                        help='calculate the weights for entire catalog')
    parser.add_argument('-l', '--loglevel', type=str,
                        help='log level [default: WARNING]')
    parser.add_argument('--nproc', type=str,
                        help='the number of processes to run in parallel [default: 4]')
    parser.add_argument('--model', type=str, help='model name',
                        required=False)
    parser.add_argument('--exp', type=str, help='experiment name',
                        required=False)
    parser.add_argument('--source', type=str, help='source name',
                        required=False)
    parser.add_argument('--resolution', type=str, help='resolution of the grid',
                        required=False)
    parser.add_argument('--rebuild', type=str, help='force rebuilding of area and weight files',
                        required=False)
    return parser.parse_args(args)


def check_input_parameters(full_catalogue, models, experiments, sources):
    """Check input parameters and exit if necessary"""
    if not full_catalogue and (not models or not experiments or not sources):
        logger.error("If you do not want to generate weights for the entire catalog, "
                     "you must provide non-empty lists of models, experiments, and sources.")
        sys.exit(1)
    elif full_catalogue:
        logger.info("The weights will be generated for the entire catalog.")
    else:
        logger.info("The weights will be generated for the specified models, experiments, and sources.")

def ensure_list(value):
    """Ensure that the input is a list"""
    return [value] if not isinstance(value, list) else value

def calculate_weights(logger, model, exp, source, regrid, zoom, nproc, rebuild):
    """Calculate weights for a specific combination of model, experiment, source, regrid, and zoom"""
    logger.debug(f"The weights are calculating for {model} {exp} {source} {regrid} {zoom}")
    try:
        Reader(model=model, exp=exp, source=source, regrid=regrid, zoom=zoom, nproc=nproc, rebuild=rebuild)
    except Exception as e:
        logger.error(f"An unexpected error occurred for source {model} {exp} {source} {regrid} {zoom}: {e}")

def generate_weights(logger, full_catalogue, resolutions, models, experiments, sources, nproc, zoom_max, rebuild):
    logger.info("Weight generation is started.")
    if full_catalogue:
        models, experiments, sources = [], [], []
    models = ensure_list(models)
    experiments = ensure_list(experiments)
    sources = ensure_list(sources)
    
    for reso in resolutions:
        for model in models or inspect_catalogue():
            for exp in experiments or inspect_catalogue(model=model):
                for source in sources or inspect_catalogue(model=model, exp=exp):
                    for zoom in range(zoom_max):
                        calculate_weights(logger, model, exp, source, reso, zoom, nproc, rebuild)

if __name__ == "__main__":
    args = parse_arguments(sys.argv[1:])
    
    file = get_arg(args, 'config', 'config/weights_config.yml.yml')
    print('Reading configuration yaml file..')
    config = load_yaml(file)

    loglevel = get_arg(args, 'loglevel', config['loglevel'])
    logger = log_configure(log_name='Weights Generator', log_level=loglevel)

    models = get_arg(args, 'model', config['data']['models'])
    experiments = get_arg(args, 'exp', config['data']['experiments'])
    sources = get_arg(args, 'source', config['data']['sources'])
    resolutions = get_arg(args, 'resolution', config['data']['resolutions'])
    zoom_max = get_arg(args, 'zoom_max', config['data']['zoom_max'])
    rebuild = get_arg(args, 'rebuild', config['rebuild'])
    full_catalogue = get_arg(args, 'catalogue', config['full_catalogue'])
    nproc = get_arg(args, 'nproc', config['nproc'])
    
    check_input_parameters(full_catalogue, models, experiments, sources)
    generate_weights(logger, full_catalogue, resolutions, models, experiments, sources, nproc, zoom_max, rebuild)