"""
Utility functions for the CLI
"""
import argparse
import os
import gc
import pandas as pd
import xarray as xr
from dask.distributed import Client, LocalCluster
from aqua.logger import log_configure, log_history
from aqua.util import load_yaml, get_arg, convert_units
from aqua.util import ConfigPath
from aqua import Reader

def template_parse_arguments(parser: argparse.ArgumentParser):
    """
    Add the default arguments to the parser.

    Args:
        parser: argparse.ArgumentParser

    Returns:
        argparse.ArgumentParser
    """
    parser.add_argument("--loglevel", "-l", type=str,
                        required=False, help="loglevel")
    parser.add_argument("--catalog", type=str,
                        required=False, help="catalog name")
    parser.add_argument("--model", type=str,
                        required=False, help="model name")
    parser.add_argument("--exp", type=str,
                        required=False, help="experiment name")
    parser.add_argument("--source", type=str,
                        required=False, help="source name")
    parser.add_argument("--config", "-c", type=str,
                        help='yaml configuration file')
    parser.add_argument("--nworkers", "-n", type=int,
                        required=False, help="number of workers")
    parser.add_argument("--cluster", type=str,
                        required=False, help="cluster address")
    parser.add_argument("--regrid", type=str,
                        required=False, help="target regrid resolution")
    parser.add_argument("--outputdir", type=str,
                        required=False, help="output directory")

    return parser


def open_cluster(nworkers, cluster, loglevel: str = 'WARNING'):
    """
    Open a dask cluster if nworkers is provided, otherwise connect to an existing cluster.

    Args:
        nworkers (int): number of workers
        cluster (str): cluster address
        loglevel (str): logging level

    Returns:
        client (dask.distributed.Client): dask client
        cluster (dask.distributed.LocalCluster): dask cluster
        private_cluster (bool): whether the cluster is private
    """

    logger = log_configure(log_name='Cluster', log_level=loglevel)

    private_cluster = False
    if nworkers or cluster:
        if not cluster:
            cluster = LocalCluster(n_workers=nworkers, threads_per_worker=1)
            logger.info(f"Initializing private cluster {cluster.scheduler_address} with {nworkers} workers.")
            private_cluster = True
        else:
            logger.info(f"Connecting to cluster {cluster}.")
        client = Client(cluster)
    else:
        client = None

    return client, cluster, private_cluster


def close_cluster(client, cluster, private_cluster, loglevel: str = 'WARNING'):
    """
    Close the dask cluster and client.

    Args:
        client (dask.distributed.Client): dask client
        cluster (dask.distributed.LocalCluster): dask cluster
        private_cluster (bool): whether the cluster is private
        loglevel (str): logging level
    """
    logger = log_configure(log_name='Cluster', log_level=loglevel)

    if client:
        client.close()
        logger.debug("Dask client closed.")

    if private_cluster:
        cluster.close()
        logger.debug("Dask cluster closed.")


def load_diagnostic_config(diagnostic: str, args: argparse.Namespace,
                           default_config: str = "config.yaml",
                           loglevel: str = 'WARNING'):
    """
    Load the diagnostic configuration file and return the configuration dictionary.

    Args:
        diagnostic (str): diagnostic name
        args (argparse.Namespace): arguments of the CLI. "config" argument can modify the default configuration file.
        default_config (str): default name configuration file (yaml format)
        loglevel (str): logging level. Default is 'WARNING'.

    Returns:
        dict: configuration dictionary
    """
    if args.config:
        filename = args.config
    else:
        configdir = ConfigPath(loglevel=loglevel).configdir
        filename = os.path.join(configdir, "diagnostics", diagnostic, default_config)

    return load_yaml(filename)


def merge_config_args(config: dict, args: argparse.Namespace,
                      loglevel: str = 'WARNING') -> dict:
    """
    Merge the configuration dictionary with the arguments of the CLI.

    Args:
        config (dict): configuration dictionary
        args (argparse.Namespace): arguments of the CLI
        loglevel (str): logging level. Default is 'WARNING'.

    Returns:
        dict: merged configuration dictionary
    """
    logger = log_configure(log_name='merge_config_args', log_level=loglevel)
    datasets = config['datasets']

    # Override the first dataset in the config file if provided in the command line
    datasets[0]['catalog'] = get_arg(args, 'catalog', datasets[0]['catalog'])
    datasets[0]['model'] = get_arg(args, 'model', datasets[0]['model'])
    datasets[0]['exp'] = get_arg(args, 'exp', datasets[0]['exp'])
    datasets[0]['source'] = get_arg(args, 'source', datasets[0]['source'])

    config['output']['outputdir'] = get_arg(args, 'outputdir', config['output']['outputdir'])

    logger.debug("Analyzing models:")
    for model in config['datasets']:
        logger.debug(f"  - {model['catalog']} {model['model']} {model['exp']} {model['source']}")

    if 'references' in config:
        logger.debug("Using reference data:")
        for ref in config['references']:
            logger.debug(f"  - {ref['catalog']} {ref['model']} {ref['exp']} {ref['source']}")

    return config


def convert_data_units(data, var: str, units: str, loglevel: str = 'WARNING'):
    """
    Make sure that the data is in the correct units.

    Args:
        data (xarray Dataset or DataArray): The data to be checked.
        var (str): The variable to be checked.
        units (str): The units to be checked.
    """
    logger = log_configure(log_name='check_data', log_level=loglevel)

    data_to_fix = data[var] if isinstance(data, xr.Dataset) else data
    final_units = units
    initial_units = data_to_fix.units

    conversion = convert_units(initial_units, final_units)

    factor = conversion.get('factor', 1)
    offset = conversion.get('offset', 0)

    if factor != 1 or offset != 0:
        logger.debug('Converting %s from %s to %s',
                     var, initial_units, final_units)
        data_to_fix = data_to_fix * factor + offset
        data_to_fix.attrs['units'] = final_units
        log_history(data_to_fix, f"Converting units of {var}: from {initial_units} to {final_units}")
    else:
        logger.debug('Units of %s are already in %s', var, final_units)
        return data

    if isinstance(data, xr.Dataset):
        data_fixed = data.copy()
        data_fixed[var] = data_to_fix
    else:
        data_fixed = data_to_fix

    return data_fixed


def retrieve_merge_ensemble_data(
    variable: str = None,
    region: str = None,
    ens_dim: str = "ensemble",
    data_path_list: list[str] = None,
    catalog_list: list[str] = None,
    models_catalog_list: list[str] = None,
    exps_catalog_list: list[str] = None,
    sources_catalog_list: list[str] = None,
    startdate: str = None,
    enddate: str = None,
    log_level: str = "WARNING",
):
    """
    Retrieves, merges, and slices datasets based on specified models, experiments,
    sources, and time boundaries.

    This function reads data for a given variable (`variable`) from multiple models, experiments,
    and sources, combines the datasets along the specified "ensemble" dimension along with their indices, and slices
    the merged dataset to the given start and end dates. The ens_dim can given any customized name for the ensemble dimension.

    There are following two ways to load the datasets with function.
    a) with xarray.open_dataset
    b) with AQUA Reader class

    Args:
        variable (str): The variable to retrieve data. Defaults to None.
        In the case a):
            data_path_list (list of str): list of paths for data to be loaded by xarray.
        In the case b):
            region (str): This variable is specific to the Zonal averages. Defaults to None.
            catalog_list (list): A list of AQUA catalog. Default to None.
            models_catalog_list (list): A list of model names. Each model corresponds to an
                experiment and source in the `exps` and `sources` lists, respectively.
                Defaults to None.
            exps_catalog_list (list): A list of experiment names. Each experiment corresponds
                to a model and source in the `models` and `sources` lists, respectively.
                Defaults to None.
            sources_catalog_list (list): A list of data source names. Each source corresponds
                to a model and experiment in the `models` and `exps` lists, respectively.
                Defaults to None.

        Specific to the timeseries datasets:
            startdate (str or datetime): The start date for slicing the merged dataset.
                If None is provided, the ensemble members are merged w.r.t to their time-interval. Defaults to None.
            enddate (str or datetime): The end date for slicing the merged dataset.
                If None is provided, the ensemble members are merged w.r.t to their time-interval. Defaults to None.
    Returns:
            xarray.Dataset: The merged dataset containing data from all specified models,
                experiments, and sources, concatenated along `ens_dim`
    """
    logger = log_configure(log_name="retrieve_merge_ensemble_data", log_level=log_level)
    logger.info("Loading and merging the ensemble dataset")

    # in case if the list of paths of netcdf dataset is given
    # then load via xarray.open_dataset function
    # return ensemble dataset with with ensemble dimension ens_dim with individual indexes
    # temporary list to append the datasets and later concat the list to merged dataset along ens_dim
    tmp_dataset_list = []
    tmp_min_date_list = []
    tmp_max_date_list = []
    # Method (a): To load and merge the dataset via file paths
    if data_path_list is not None:
        for i, f in enumerate(data_path_list):
            tmp_dataset = xr.open_dataset(
                f, drop_variables=[var for var in xr.open_dataset(f).data_vars if var != variable]
            ).expand_dims({ens_dim: [i]})
            tmp_dataset_list.append(tmp_dataset)
            if "time" in tmp_dataset.dims:
                if startdate is not None and enddate is not None:
                    tmp_dataset = tmp_dataset.sel(time=slice(startdate, enddate))
                else:
                    tmp_min_date_list.append(pd.to_datetime(tmp_dataset.time.values[0]))
                    tmp_max_date_list.append(pd.to_datetime(tmp_dataset.time.values[-1]))
        ens_dataset = xr.concat(tmp_dataset_list, dim=ens_dim)
    # Method (b):
    # else if check the models, exps and sources are given from the catalog in the forms of lists
    # then use the AQUA.Reader class to load the data
    elif (
        models_catalog_list is not None
        and exps_catalog_list is not None
        and sources_catalog_list is not None
    ):
        if catalog_list is not None: 
            for i, model in enumerate(models_catalog_list):
                # check if region variable is defined
                if region is not None:
                    tmp_reader = Reader(
                        catalog=catalog_list[i],
                        model=model,
                        exp=exps_catalog_list[i],
                        source=sources_catalog_list[i],
                        areas=False,
                        region=region,
                    )
                else:
                    tmp_reader = Reader(
                        catalog=catalog_list[i],
                        model=model,
                        exp=exps_catalog_list[i],
                        source=sources_catalog_list[i],
                        areas=False,
                    )
                tmp_dataset = tmp_reader.retrieve(var=variable)
                tmp_dataset_expended = tmp_dataset.expand_dims(ensemble=[i])
                tmp_dataset_list.append(tmp_dataset_expended)
        else:
            for i, model in enumerate(models_catalog_list):
                # check if region variable is defined
                if region is not None:
                    tmp_reader = Reader(
                        model=model,
                        exp=exps_catalog_list[i],
                        source=sources_catalog_list[i],
                        areas=False,
                        region=region,
                    )
                else:
                    tmp_reader = Reader(
                        model=model,
                        exp=exps_catalog_list[i],
                        source=sources_catalog_list[i],
                        areas=False,
                    )
                tmp_dataset = tmp_reader.retrieve(var=variable)
                tmp_dataset_expended = tmp_dataset.expand_dims(ensemble=[i])
                tmp_dataset_list.append(tmp_dataset_expended)
        if "time" in tmp_dataset.dims:
            if startdate is not None and enddate is not None:
                tmp_dataset = tmp_dataset.sel(time=slice(startdate, enddate))
            else:
                tmp_min_date_list.append(pd.to_datetime(tmp_dataset.time.values[0]))
                tmp_max_date_list.append(pd.to_datetime(tmp_dataset.time.values[-1]))

        # concatenate along the ensemble dimension
        ens_dataset = xr.concat(tmp_dataset_list, dim=ens_dim)
        # delete tmp varaibles
        del tmp_reader, tmp_dataset_expended
    else:
        # No data is given
        raise NoDataError("No Data is provided to retreieve and merge for ensemble")

    if tmp_min_date_list and tmp_max_date_list:
        common_startdate = max(tmp_min_date_list)
        common_enddate = min(tmp_max_date_list)
    # delete all tmp varaibles
    del tmp_dataset_list, tmp_min_date_list, tmp_max_date_list, tmp_dataset
    gc.collect()
    # check if the ensemble dataset is a timeseries dataset
    # then return enemble dataset
    if "time" in ens_dataset.dims:
        logger.info("Finished loading the ensemble timeseries datasets")
        if startdate is not None and enddate is not None:
            common_startdate = startdate
            common_enddate = enddate
        return ens_dataset.sel(time=slice(common_startdate, common_enddate))
    else:
        # the ensemble dataset is not a timeseries
        logger.info("Finished loading the ensemble datasets")
        return ens_dataset
