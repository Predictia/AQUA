#!/usr/bin/env python3
"""
Command-line interface for ensemble atmglobalmean diagnostic.

This CLI allows to plot a map of aqua analysis atmglobalmean
defined in a yaml configuration file for multiple models.
"""
import argparse
import os
import sys
import gc
import xarray as xr
from dask.distributed import Client, LocalCluster
from dask.utils import format_bytes
from aqua import Reader
from aqua.util import load_yaml, get_arg, ConfigPath
from aqua.exceptions import NotEnoughDataError, NoDataError, NoObservationError
from aqua.logger import log_configure

from aqua.diagnostics import EnsembleLatLon

def parse_arguments(args):
    """Parse command line arguments."""

    parser = argparse.ArgumentParser(description="Ensemble atmglobalmean map CLI")

    parser.add_argument("-c", "--config",
                        type=str, required=False,
                        help="yaml configuration file")
    parser.add_argument('-n', '--nworkers', type=int,
                        help='number of dask distributed workers')
    parser.add_argument("--loglevel", "-l", type=str,
                        required=False, help="loglevel")

    # These will override the first one in the config file if provided
    parser.add_argument("--catalog", type=str,
                        required=False, help="catalog name")
    parser.add_argument("--model", type=str,
                        required=False, help="model name")
    parser.add_argument("--exp", type=str,
                        required=False, help="experiment name")
    parser.add_argument("--source", type=str,
                        required=False, help="source name")
    parser.add_argument("--outputdir", type=str,
                        required=False, help="output directory")
    parser.add_argument("--cluster", type=str, 
                        required=False, help="dask cluster address")

    return parser.parse_args(args)

def retrieve_data(variable=None, models=None, exps=None, sources=None, ens_dim="Ensembles"):
    """
    Retrieves and merges datasets based on specified models, experiments, and sources.

    This function reads data for a given variable (` variable`) from multiple models, experiments, 
    and sources, combines them along the specified ensemble dimension, and returns the 
    merged dataset.

    Args:
        variable (str): The variable to retrieve data for. Defaults to None.
        models (list): A list of model names. Each model corresponds to an 
            experiment and source in the `exps` and `sources` lists, respectively. 
            Defaults to None.
        exps (list): A list of experiment names. Each experiment corresponds 
            to a model and source in the `models` and `sources` lists, respectively. 
            Defaults to None.
        sources (list): A list of data source names. Each source corresponds 
            to a model and experiment in the `models` and `exps` lists, respectively. 
            Defaults to None.
        ens_dim (str, optional): The name of the dimension along which the datasets 
            are concatenated. Defaults to "Ensembles".

    Returns:
        xarray.Dataset: A merged dataset containing data from all specified models, 
        experiments, and sources, concatenated along the `ens_dim` dimension.
    """
    dataset_list = []
    if models is None or exps is None or sources is None:
        raise NoDataError("No models, exps or sources provided")
    else:
        for i, model in enumerate(models):
            reader = Reader(model=model, exp=exps[i], source=sources[i], areas=False)
            data = reader.retrieve(var=variable)
            dataset_list.append(data)
    merged_dataset = xr.concat(dataset_list, ens_dim)
    del reader
    del data
    del dataset_list
    gc.collect()
    return merged_dataset


if __name__ == '__main__':

    args = parse_arguments(sys.argv[1:])

    loglevel = get_arg(args, "loglevel", "WARNING")
    logger = log_configure(loglevel, 'CLI multi-model ensemble calculation of atmglobalmean')
    logger.info("Running multi-model ensemble calculation of atmglobalmean")

    # Load configuration file
    configdir = ConfigPath(loglevel=loglevel).configdir
    default_config = os.path.join(configdir, "diagnostics", "ensemble",
                                  "config_atmglobalmean_ensemble.yaml")
    file = get_arg(args, "config", default_config)
    logger.info(f"Reading configuration file {file}")
    config = load_yaml(file)

    # Initialize the Dask cluster
    nworkers = get_arg(args, 'nworkers', None)
    config_cluster = get_arg(args, 'cluster', None)

    # If nworkers is not provided, use the value from the config
    if nworkers is None or config_cluster is None:
        config_cluster = config['cluster'].copy()
    if nworkers is not None:
        config_cluster['nworkers'] = nworkers

    cluster = LocalCluster(n_workers=config_cluster['nworkers'], threads_per_worker=1)
    client = Client(cluster)

    # Get the Dask dashboard URL
    logger.info("Dask Dashboard URL: %s", client.dashboard_link)
    workers = client.scheduler_info()["workers"]
    worker_count = len(workers)
    total_memory = format_bytes(
        sum(w["memory_limit"] for w in workers.values() if w["memory_limit"]))
    memory_text = f"Workers={worker_count}, Memory={total_memory}"
    logger.info(memory_text)

    variable = config['variable']
    logger.info(f"Variable under consideration: {variable}")
    outputdir = get_arg(args, "outputdir", config["outputdir"])

    plot_options = config.get("plot_options", {})

    logger.info(f"Loading {variable} atmglobalmean 2D-data")

    models = config['datasets']
    model_list = []
    exp_list = []
    source_list = []
    if models != None:
        models[0]['catalog'] = get_arg(args, 'catalog', models[0]['catalog'])
        models[0]['model'] = get_arg(args, 'model', models[0]['model'])
        models[0]['exp'] = get_arg(args, 'exp', models[0]['exp'])
        models[0]['source'] = get_arg(args, 'source', models[0]['source'])
        for model in models:
            model_list.append(model['model'])
            exp_list.append(model['exp'])
            source_list.append(model['source'])

    atm_dataset = retrieve_data(variable, models=model_list, exps=exp_list, sources=source_list)

    atmglobalmean_ens = EnsembleLatLon(var= variable, dataset=atm_dataset, outputdir=outputdir, plot_options=plot_options)
    atmglobalmean_ens.run()
    logger.info(f"Finished Ensemble_latLon diagnostic for {variable}.")
    # Close the Dask client and cluster
    client.close()
    cluster.close()
