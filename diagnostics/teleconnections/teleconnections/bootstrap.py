"""
Module to evaluate the confidence intervals of the teleconnections using bootstrapping.
"""
import numpy as np
import xarray as xr

from aqua.logger import log_configure
from . import reg_evaluation, cor_evaluation


def bootstrap_teleconnections(reg: xr.DataArray,
                              index: xr.DataArray,
                              index_ref: xr.DataArray,
                              data_ref: xr.DataArray,
                              n_bootstraps=1000,
                              concordance=0.5,
                              statistic=None,
                              loglevel='WARNING',
                              **eval_kwargs):
    """
    Bootstrap the regression and correlation maps.

    Args:
        reg (xr.DataArray): Regression map of the dataset
        index (xr.DataArray): Index of the dataset
        index_ref (xr.DataArray): Index of the reference dataset
        data_ref (xr.DataArray): Data of the reference dataset to perform the regression
                                 or correlation with.
        n_bootstraps (int): Number of bootstraps to perform. Default is 1000.
        concordance (float): Concordance threshold. Default is 0.5.
        statistic (str): Statistic to compute. Default is None.
                         Available options are 'reg' and 'cor'.
        loglevel (str): Logging level. Default is 'WARNING'.
        eval_kwargs (dict): Additional keyword arguments to pass to the evaluation function.
    """
    logger = log_configure(loglevel, 'Bootstrap teleconnections')

    if statistic is None:
        raise ValueError('No statistic was provided. Please provide a statistic to compute (reg or cor).')

    # Build the bootstrap maps DataArray
    bootstrap_maps = xr.DataArray(np.zeros((n_bootstraps,) + reg.shape),
                                  coords=[range(n_bootstraps)] + [coord for coord in reg.coords.values()],
                                  dims=['bootstrap'] + [dim for dim in reg.dims])

    # Bootstrap the maps
    for i in range(n_bootstraps):
        logger.debug(f'Bootstrap {i+1}/{n_bootstraps}')

        boot_time = np.random.choice(index_ref.time.values, index.time.size, replace=True)

        boot_index = index_ref.sel(time=boot_time)
        boot_data = data_ref.sel(time=boot_time)

        if statistic == 'reg':
            bootstrap_maps[i] = reg_evaluation(indx=boot_index, data=boot_data, **eval_kwargs)
        elif statistic == 'cor':
            bootstrap_maps[i] = cor_evaluation(indx=boot_index, data=boot_data, **eval_kwargs)

    # Evaluate the percentile confidence intervals
    lower = bootstrap_maps.quantile(1-concordance/2, dim='bootstrap')
    upper = bootstrap_maps.quantile(concordance/2, dim='bootstrap')

    return lower, upper


def build_confidence_mask(reg: xr.DataArray, lower: xr.DataArray, upper: xr.DataArray,
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
        mask = ((reg <= upper) & (reg >= lower)).astype(int)
    else:  # Mask the discordance regions
        mask = ((reg >= upper) | (reg <= lower)).astype(int)

    return mask
