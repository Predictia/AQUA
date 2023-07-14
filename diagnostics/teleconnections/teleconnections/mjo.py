"""
Module to evaluate the MJO teleconnection.
"""
import xarray as xr


def mjo_hovmoller(data: xr.DataArray):
    """
    Prepare the data for a MJO Hovmoller plot.
    """