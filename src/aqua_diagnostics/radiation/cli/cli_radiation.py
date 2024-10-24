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
from aqua.diagnostics import GlobalBiases, Timeseries, Radiation

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
    file = get_arg(args, "config", "global_bias_config.yaml")
    logger.info(f"Reading configuration file {file}")
    config = load_yaml(file)

    # Acquiring model, experiment and source
    catalog_data = get_arg(args, 'catalog', config['data']['catalog'])
    model_data = get_arg(args, 'model', config['data']['model'])
    exp_data = get_arg(args, 'exp', config['data']['exp'])
    source_data = get_arg(args, 'source', config['data']['source'])
    
    startdate_data = config['diagnostic_attributes'].get('startdate_data', None)  #aggiungere default
    enddate_data = config['diagnostic_attributes'].get('enddate_data', None)

    if startdate_data is None:
        startdate_data = self.data.time[0].values  

    if enddate_data is None:
        enddate_data = self.data.time[-1].values 


    # Acquiring model, experiment and source for reference data
    catalog_obs = config['obs']['catalog']
    model_obs = config['obs']['model']
    exp_obs = config['obs']['exp']
    source_obs = config['obs']['source']

    startdate_obs = config['diagnostic_attributes'].get('startdate_obs')
    enddate_obs = config['diagnostic_attributes'].get('enddate_obs')

    if startdate_obs is None:
        startdate_obs = self.data.time[0].values  

    if enddate_data is None:
        enddate_data = self.data.time[-1].values 

    #create output directory
    outputdir = get_arg(args, "outputdir", config["outputdir"])
    out_pdf = os.path.join(outputdir, 'pdf')
    out_netcdf = os.path.join(outputdir, 'netcdf')
    create_folder(out_pdf, loglevel )
    create_folder(out_netcdf, loglevel)

    variables = config['diagnostic_attributes'].get('variables', [])
    
    names = OutputSaver(diagnostic='radiation', model=model_data, exp=exp_data, loglevel=loglevel)

    try:
        reader = Reader(catalog = catalog_data, model=model_data, exp=exp_data, source=source_data, startdate=startdate_data, enddate=enddate_data, regrid='r100')
        data = reader.retrieve()
        data = data.regrid(data[variables])
    except Exception as e:
        logger.error(f"No model data found: {e}")
        logger.critical("Global mean biases diagnostic is terminated.")
        sys.exit(0)

    try:
        reader_ = Reader(catalog = catalog_obs, model=model_obs, exp=exp_obs, source=source_obs, startdate=startdate_obs, enddate=enddate_obs, regrid='r100')
        data_obs = reader_obs.retrieve()
        data_obs = data_obs.regrid(data_obs[variables])
    except Exception as e:
        logger.error(f"No observation data found: {e}")


    #global biases
    for var_name in variables:
        logger.info(f"Producing bias map for {var_name}...")
        try:
            global_biases = GlobalBiases(data=data, data_ref = data_obs, var_name=var_name, plev=plev, loglevel=loglevel)
 
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")

    logger.info("Global Biases diagnostic is terminated.")