# Imports for CLI diagnostic
import sys
import os
import argparse
from dask.distributed import Client, LocalCluster
import pandas as pd

import dask.distributed as dd
from dask.utils import format_bytes

from aqua.util import load_yaml, get_arg, OutputSaver, ConfigPath, to_list
from aqua import Reader
from aqua.exceptions import NotEnoughDataError, NoDataError, NoObservationError
from aqua.logger import log_configure
from aqua.diagnostics import sshVariability

def parse_arguments(args):
    """Parse command line arguments for Global Biases CLI."""
    parser = argparse.ArgumentParser(description='Global Biases CLI')
    parser.add_argument('-c', '--config', type=str, required=False, help='YAML configuration file')
    parser.add_argument('-n', '--nworkers', type=int, help='Number of Dask distributed workers')
    parser.add_argument("--loglevel", "-l", type=str, help="Logging level")

    # Arguments to override configuration file settings
    parser.add_argument("--catalog", type=str, required=False, help="Catalog name")
    parser.add_argument('--model', type=str, help='Model name')
    parser.add_argument('--exp', type=str, help='Experiment name')
    parser.add_argument('--source', type=str, help='Source name')
    parser.add_argument('--outputdir', type=str, help='Output directory')
    parser.add_argument("--cluster", type=str, required=False, help="dask cluster address")
    parser.add_argument("--regrid", type=str, required=False, help="Regrid the source data to a specified grid")

    return parser.parse_args(args)

def main():
    args = parse_arguments(sys.argv[1:])
    loglevel = get_arg(args, "loglevel", "WARNING")
    logger = log_configure(loglevel, 'CLI SSH Variability')
    logger.info("Starting SSH Variablility diagnostic")

    # Load configuration file
    configdir = ConfigPath(loglevel=loglevel).configdir
    default_config = os.path.join(configdir, "diagnostics", "ssh",
                                  "config_ssh.yaml")
    file = get_arg(args, "config", default_config)
    logger.info(f"Reading configuration file {file}")
    config = load_yaml(file)
    
    # Configuration options for model data
    catalog_data = get_arg(args, 'catalog', config['data']['catalog'])
    model_data = get_arg(args, 'model', config['data']['model'])
    exp_data = get_arg(args, 'exp', config['data']['exp'])
    source_data = get_arg(args, 'source', config['data']['source'])
    startdate_data = config['data'].get('startdate')
    enddate_data = config['data'].get('enddate')
    #zoom = get_arg(args, 'zoom', config['data']['zoom'])

    # Configuation options for observational data 
    catalog_obs = get_arg(args, 'catalog', config['obs']['catalog'])
    model_obs = get_arg(args, 'model', config['obs']['model'])
    exp_obs = get_arg(args, 'exp', config['obs']['exp'])
    source_obs = get_arg(args, 'source', config['obs']['source'])
    startdate_obs = config['obs'].get('startdate')
    enddate_obs = config['obs'].get('enddate')

    outputdir = get_arg(args, 'outputdir', config['outputdir'])

    # TODO: Implement these features 
    #rebuild = config['output'].get("rebuild")
    #filename = config['output'].get("filename")
    #save_netcdf = config['output'].get("save_netcdf")
    #dpi = config['output'].get("dpi")

    variable = config['variable']

    regrid = get_arg(args, 'regrid', config['plot_options'].get('regrid'))

    logger.debug(f"Data read from Catalog: {catalog_data}; Model: {model_data}; Exp: {exp_data}; Source: {source_data}; Regrid: {regrid}")
    logger.debug(f"Observations read from Catalog: {catalog_obs}; Model: {model_obs}; Exp: {exp_obs}; Source: {source_obs}; Regrid: {regrid}")

    # Initialize the Dask cluster
    nworkers = get_arg(args, 'nworkers', None)
    config_cluster = get_arg(args, 'cluster', None)
    # If nworkers is not provided, use the value from the config
    if nworkers is None or config_cluster is None:
        config_cluster = config['cluster'].copy()
    if nworkers is not None:
        config_cluster['nworkers'] = nworkers
    cluster = LocalCluster(n_workers=config_cluster['nworkers'], threads_per_worker=1)
    #cluster = LocalCluster(n_workers=config['cluster']['nworkers'], threads_per_worker=1)
    client = Client(cluster)
    # Get the Dask dashboard URL
    logger.info("Dask Dashboard URL: %s", client.dashboard_link)
    workers = client.scheduler_info()["workers"]
    worker_count = len(workers)
    total_memory = format_bytes(
        sum(w["memory_limit"] for w in workers.values() if w["memory_limit"]))
    # total_memory = format_bytes(
    #     sum(config["dask_cluster"]["memory_limit"] for w in workers.values() if "memory_limit" in config["dask_cluster"]))
    memory_text = f"Workers={worker_count}, Memory={total_memory}"
    logger.info(memory_text)

    # Retrieve model data and handle potential errors
    try:
        reader = Reader(catalog=catalog_data, model=model_data, exp=exp_data, source=source_data,
                        startdate=startdate_data, enddate=enddate_data, regrid=regrid, loglevel=loglevel)
        data = reader.retrieve(var=variable)
        data = data[variable]
        if regrid:
            data = reader.regrid(data)
        else:
            logger.warning(
            "No regridding applied. Data is in native grid, "
            "this could lead to errors in the ssh variability calculation if the data is not in the same grid as the reference data."
            )

    except Exception as e:
        logger.error(f"No model data found: {e}")
        sys.exit("SSH diagnostic terminated.")
        
    # Retrieve observational data and handle potential errors
    try:
        reader_obs = Reader(catalog=catalog_obs, model=model_obs, exp=exp_obs, source=source_obs,
                            startdate=startdate_obs, enddate=enddate_obs, regrid=regrid, loglevel=loglevel,fix=True)
        data_obs = reader_obs.retrieve(var=variable)
        print(data_obs)
        data_obs = data_obs[variable]

        if regrid:
            data_obs = reader_obs.regrid(data_obs)
        else:
            logger.warning(
            "No regridding applied. Data is in native grid, "
            "this could lead to errors in the ssh variability calculation if the data is not in the same grid as the model data."
            )

    except Exception as e:
        logger.error(f"No observation data found: {e}")
        sys.exit("SSH diagnostic terminated.")
    
    ssh_std = sshVariability(variable=variable, data_ref=data_obs, data_model=data, name_ref=model_obs, name_model=model_data, exp_ref=exp_obs, exp_model=exp_data, startdate_model=startdate_data, enddate_model=enddate_data, startdate_ref=startdate_obs, enddate_ref=enddate_obs, outputdir=outputdir)
    ssh_std.run()
    logger.info("Finished SSH diagnostic.")
    # Close the Dask client and cluster
    client.close()
    cluster.close()
    #if client:
    #    client.close()
    #    cluster.close()
    #    logger.debug("Dask client closed.")




if __name__ == '__main__':
    main()
