"""
Module to evaluate the confidence intervals of the teleconnections using bootstrapping.
"""
import numpy as np
import xarray as xr

from aqua.logger import log_configure
from teleconnections.statistics import reg_evaluation, cor_evaluation


import numpy as np
import xarray as xr


def bootstrap_teleconnections(map: xr.DataArray,
                              index: xr.DataArray,
                              index_ref: xr.DataArray,
                              data_ref,
                              n_bootstraps=1000,
                              concordance=0.05,
                              statistic=None,
                              loglevel='WARNING',
                              **eval_kwargs):
    """
    Bootstrap the regression and correlation maps.

    Args:
        map (xr.DataArray): Map of the dataset, can be regression or correlation
        index (xr.DataArray): Index of the dataset
        index_ref (xr.DataArray): Index of the reference dataset
        data_ref (xr.DataArray): Data of the reference dataset to perform the regression
                                 or correlation with.
        n_bootstraps (int): Number of bootstraps to perform. Default is 1000.
        concordance (float): Concordance threshold. Default is 0.5.
        statistic (str): Statistic to compute. Default is None.
                         Available options are 'reg' and 'cor'.
        season (str): Season to compute the statistic. Default is None.
        loglevel (str): Logging level. Default is 'WARNING'.
        eval_kwargs (dict): Additional keyword arguments to pass to the evaluation function.
    """
    logger = log_configure(loglevel, 'Bootstrap teleconnections')

    if statistic is None:
        raise ValueError('No statistic was provided. Please provide a statistic to compute (reg or cor).')

    if isinstance(data_ref, xr.Dataset):
        data_ref = data_ref[list(data_ref.keys())[0]]

    # Build the bootstrap maps DataArray
    # bootstrap_maps = xr.DataArray(np.zeros((n_bootstraps,) + map.shape),
    #                               coords=[range(n_bootstraps)] + [coord for coord in map.coords.values()],
    #                               dims=['bootstrap'] + [dim for dim in map.dims])
    bootstrap_maps = xr.DataArray(np.zeros((n_bootstraps,) + data_ref.isel(time=0).shape),
                                  coords=[range(n_bootstraps)] + [coord for coord in data_ref.coords.values() if coord.name != 'time'],
                                  dims=['bootstrap'] + [dim for dim in data_ref.dims if dim != 'time'])

    # Bootstrap the maps
    for i in range(n_bootstraps):
        logger.debug(f'Bootstrap {i+1}/{n_bootstraps}')

        boot_time = np.random.choice(index_ref.time.values, index.time.size, replace=True)

        boot_index = index_ref.sel(time=boot_time)
        boot_data = data_ref.sel(time=boot_time)

        if statistic == 'reg':
            bootstrap_maps.loc[dict(bootstrap=i)] = reg_evaluation(indx=boot_index, data=boot_data, **eval_kwargs)
        elif statistic == 'cor':
            bootstrap_maps.loc[dict(bootstrap=i)] = cor_evaluation(indx=boot_index, data=boot_data, **eval_kwargs)

    # Evaluate the percentile confidence intervals
    lower = bootstrap_maps.quantile(1-concordance/2, dim='bootstrap')
    upper = bootstrap_maps.quantile(concordance/2, dim='bootstrap')

    return lower, upper


def build_confidence_mask(map: xr.DataArray, lower: xr.DataArray, upper: xr.DataArray,
                          mask_concordance=True):
    """
    Build the confidence masks based on the lower and upper percentiles.

    Args:
        reg (xr.DataArray): Regression map of the dataset
        lower (xr.DataArray): Lower percentile map
        upper (xr.DataArray): Upper percentile map
        mask_concordance (bool): Whether to mask the concordance regions. Default is True.

    Returns:
        xr.DataArray: Confidence mask
    """
    if mask_concordance:
        mask = ((map <= upper) & (map >= lower)).astype(int)
    else:  # Mask the discordance regions
        mask = ((map >= upper) | (map <= lower)).astype(int)

    return mask
