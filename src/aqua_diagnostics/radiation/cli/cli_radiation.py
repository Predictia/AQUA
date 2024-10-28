# All necessary import for a cli diagnostic
import sys
import os
import argparse
from dask.distributed import Client, LocalCluster

import numpy as np

from aqua.util import load_yaml, get_arg, OutputSaver, create_folder
from aqua import Reader
from aqua.exceptions import NotEnoughDataError, NoDataError, NoObservationError
from aqua.logger import log_configure
from aqua.diagnostics import Radiation

def parse_arguments(args):
    """Parse command line arguments"""

    parser = argparse.ArgumentParser(description='Radiation CLI')
    parser.add_argument('-c', '--config', type=str,
                        help='yaml configuration file')
    parser.add_argument('-n', '--nworkers', type=int,
                        help='number of dask distributed workers')
    parser.add_argument("--loglevel", "-l", type=str,
                        required=False, help="loglevel")                  

    # This arguments will override the configuration file if provided
    parser.add_argument("--catalog", type=str,
                        required=False, help="catalog name")
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

    args = parse_arguments(sys.argv[1:])

    loglevel = get_arg(args, "loglevel", "WARNING")
    logger = log_configure(loglevel, 'CLI Radiation')
    logger.info("Running Radiation diagnostic")

    # Moving to the current directory so that relative paths work
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    if os.getcwd() != dname:
        os.chdir(dname)
        logger.info(f"Changing directory to {dname}")

    # Dask distributed cluster
    nworkers = get_arg(args, 'nworkers', None)
    if nworkers:
        cluster = LocalCluster(n_workers=nworkers, threads_per_worker=1)
        client = Client(cluster)
        logger.info(f"Running with {nworkers} dask distributed workers.")

    # Aquiring the configuration
    file = get_arg(args, "config", "radiation_config.yaml")
    logger.info(f"Reading configuration file {file}")
    config = load_yaml(file)

    models = config['models']
    models[0]['catalog'] = get_arg(args, 'catalog', models[0]['catalog'])
    models[0]['model'] = get_arg(args, 'model', models[0]['model'])
    models[0]['exp'] = get_arg(args, 'exp', models[0]['exp'])
    models[0]['source'] = get_arg(args, 'source', models[0]['source'])

    logger.debug("Analyzing models:")
    models_list = []
    exp_list = []
    datasets = []
    variables = config['diagnostic_attributes'].get('variables', ['-mtnlwrf', 'mtnswrf'])

    for model in models:
        try:
            reader = Reader(catalog = model['catalog'], model=model['model'], exp=model['exp'], source=model['source'])
            dataset = reader.retrieve()   
        except Exception as e:
            logger.error(f"No model data found: {e}")
            logger.critical("Radiation diagnostic is terminated.")
            sys.exit(0)
        datasets.append(dataset)
        models_list.append(model['model'])
        exp_list.append(model['exp'])

    #creating output directory
    outputdir = get_arg(args, "outputdir", config["outputdir"])
    out_pdf = os.path.join(outputdir, 'pdf')
    out_netcdf = os.path.join(outputdir, 'netcdf')
    create_folder(out_pdf, loglevel )
    create_folder(out_netcdf, loglevel)

    variables = config['diagnostic_attributes'].get('variables', [])

    names = OutputSaver(diagnostic='radiation', model= models_list[0], exp = exp_list[0], loglevel=loglevel)
    
    logger.info("Boxplot generation")
    radiation = Radiation()
    result = radiation.boxplot(datasets=datasets, model_names=models_list, variables=variables)
    if result is not None:
        fig, ax = result  
        names.generate_name(diagnostic_product='boxplot')
        names.save_pdf(fig, path=out_pdf)
