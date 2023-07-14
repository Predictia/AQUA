"""
Module to evaluate the MJO teleconnection.
"""
import xarray as xr

from aqua.logger import log_configure
from teleconnections.tools import load_namelist, area_selection


def mjo_hovmoller(data=None, **kwargs) -> xr.DataArray:
    """
    Prepare the data for a MJO Hovmoller plot.

    Args:
        data: Data to be prepared for the MJO Hovmoller plot.
              May be a xarray.DataArray or a xarray.Dataset.
        **kwargs: Keyword arguments to be passed to the function.

    KwArgs:
        loglevel (str):   Log level to be used. Default is "WARNING".
        telecname (str):  Name of the teleconnection to be evaluated.
                          Default is "MJO".
        namelist (dict):  Namelist with the teleconnection informations.
        configdir (str):  Path to the configuration directory.
        day_window (int): Number of days to be used in the smoothing window.
                          Default is 5.
    """
    loglevel = kwargs.get("loglevel", "WARNING")
    logger = log_configure(log_level=loglevel, log_name='MJO')

    if data is None:
        raise ValueError("No data provided.")

    telecname = kwargs.get("telecname", "MJO")

    namelist = kwargs.get("namelist", None)

    if namelist is None:
        logger.info("No namelist provided. Trying to load default namelist.")
        try:
            namelist = load_namelist(**kwargs)  # can take configdir
        except TypeError:  # kwargs are not accepted
            namelist = load_namelist()

    # Subselect field if data is a dataset
    if isinstance(data, xr.Dataset):
        logger.info("Subselecting var " + namelist[telecname]['field'])
        data = data[namelist[telecname]['field']]

    # Acquiring MJO box
    lat = [namelist[telecname]['latS'], namelist[telecname]['latN']]
    lon = [namelist[telecname]['lonW'], namelist[telecname]['lonE']]

    # Selecting the MJO box
    data_sel = area_selection(data, lat=lat, lon=lon)

    # Evaluating anomalies
    data_mean = data_sel.mean(dim='time', keep_attrs=True)
    data_anom = data_sel - data_mean

    # Smoothing the data
    day_window = kwargs.get("day_window", 5)
    data_anom_smooth = data_anom.rolling(time=day_window, center=True).mean()

    return data_anom_smooth
