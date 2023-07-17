"""Module for computing regression maps."""
import xarray as xr

from teleconnections.tools import _check_dim


def reg_evaluation(indx, data, dim='time'):
    """
    Evaluate regression map of a teleconnection index
    and a DataArray field

    Args:
        indx (DataArray):       index DataArray
        data (DataArray):       data DataArray

    Returns:
        reg (DataArray):        DataArray for regression map
        fig (Figure,opt):       Figure object
        ax (Axes,opt):          Axes object
    """
    _check_dim(indx, dim)
    _check_dim(data, dim)

    reg = xr.cov(indx, data, dim=dim)/indx.var(dim=dim,
                                               skipna=True).values

    return reg


def cor_evaluation(indx, data, dim='time'):
    """
    Evaluate correlation map of a teleconnection index
    and a DataArray field

    Args:
        indx (DataArray):       index DataArray
        data (DataArray):       data DataArray

    Returns:
        cor (DataArray):        DataArray for correlation map
        fig (Figure,opt):       Figure object
        ax (Axes,opt):          Axes object
    """
    _check_dim(indx, dim)
    _check_dim(data, dim)

    cor = xr.corr(indx, data, dim=dim)

    return cor
