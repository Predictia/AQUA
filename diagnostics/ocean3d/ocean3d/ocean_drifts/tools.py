"""
Global Ocean module
"""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import xarray as xr
import numpy as np
import dask.array as da
from scipy.stats import t as statt
from ocean3d import weighted_area_mean
from ocean3d import area_selection
from ocean3d import weighted_zonal_mean
from ocean3d import file_naming
from ocean3d import custom_region
from ocean3d import write_data
from ocean3d import export_fig
from aqua.logger import log_configure



def data_process_by_type(**kwargs):
    """
    Selects the type of timeseries and colormap based on the given parameters.

    Args:
        data (DataArray): Input data containing temperature (avg_thetao) and salinity (avg_so).
        anomaly (bool, optional): Specifies whether to compute anomalies. Defaults to False.
        standardise (bool, optional): Specifies whether to standardize the data. Defaults to False.
        anomaly_ref (str, optional): Reference for the anomaly computation. Valid options: "t0", "tmean". Defaults to None.

    Returns:
        process_data (Dataset): Processed data based on the selected preprocessing approach.
        type (str): Type of preprocessing approach applied
        cmap (str): Colormap to be used for the plot.
    """
    loglevel= kwargs.get('loglevel',"WARNING")
    logger = log_configure(loglevel, 'data_process_by_type')
    data = kwargs["data"]
    anomaly = kwargs["anomaly"]
    anomaly_ref = kwargs["anomaly_ref"]
    standardise = kwargs["standardise"]
    
    process_data = xr.Dataset()

    
    if anomaly:
        anomaly_ref = anomaly_ref.lower().replace(" ", "").replace("_", "")
        if not standardise:
            if anomaly_ref in ['tmean', "meantime", "timemean"]:
                cmap = "coolwarm" #"PuOr"
                for var in list(data.data_vars.keys()):
                    process_data[var] = data[var] - data[var].mean(dim='time')
                type = "anomaly wrt temporal mean"
            elif anomaly_ref in ['t0', "intialtime", "firsttime"]:
                cmap = "coolwarm" #"PuOr"
                for var in list(data.data_vars.keys()):
                    process_data[var] = data[var] - data[var].isel(time=0)
                type = "anomaly wrt initial time"
            else:
                raise ValueError(
                    "Select proper value of anomaly_ref: t0 or tmean, when anomaly = True ")
            logger.debug(f"Data processed for {type}")
        if standardise:
            if anomaly_ref in ['t0', "intialtime", "firsttime"]:
                cmap = "coolwarm" #"PuOr"
                for var in list(data.data_vars.keys()):
                    var_data = data[var] - data[var].isel(time=0)
                    var_data.attrs['units'] = 'Stand. Units'
                    # Calculate the standard anomaly by dividing the anomaly by its standard deviation along the time dimension
                    process_data[var] = var_data / var_data.std(dim="time")
                type = "Std. anomaly wrt initial time"
            elif anomaly_ref in ['tmean', "meantime", "timemean"]:
                cmap = "coolwarm" #"PuOr"
                for var in list(data.data_vars.keys()):
                    var_data = data[var] - data[var].mean(dim='time')
                    var_data.attrs['units'] = 'Stand. Units'
                    # Calculate the standard anomaly by dividing the anomaly by its standard deviation along the time dimension
                    process_data[var] = var_data / var_data.std(dim="time")
                type = "Std. anomaly wrt temporal mean"
            else:
                raise ValueError(
                    "Select proper value of type: t0 or tmean, when anomaly = True ")
            logger.debug(
                f"Data processed for {type}")

    else:
        cmap = 'jet'
        logger.debug("Data processed for Full values as anomaly = False")
        type = "Full values"

        process_data = data
    # logger.debug(f"Data processed for {type}")
    return process_data, type, cmap
    
    
def zonal_mean_trend_plot(o3d_request, loglevel= "WARNING"):
    """
    Plots spatial trends at different vertical levels for two variables.

    Args:
        data (xarray.Dataset):
            Input dataset containing a single 3D field with trends as a function of depth, latitude, and longitude.

        region (str, optional):
            Region name.

        lat_s (float, optional):
            Southern latitude bound for the region.

        lat_n (float, optional):
            Northern latitude bound for the region.

        lon_w (float, optional):
            Western longitude bound for the region.

        lon_e (float, optional):
            Eastern longitude bound for the region.

        output (bool, optional):
            Flag indicating whether to save the output figure and data. Defaults to True.

        output_dir (str, optional):
            Output directory path. Defaults to "output".

    Returns:
        None
    """
    logger = log_configure(loglevel, 'zonal_mean_trend_plot')
    data = o3d_request.get('data')
    model = o3d_request.get('model')
    exp = o3d_request.get('exp')
    source = o3d_request.get('source')
    region = o3d_request.get('region', None)
    lat_s = o3d_request.get('lat_s', None)
    lat_n = o3d_request.get('lat_n', None)
    lon_w = o3d_request.get('lon_w', None)
    lon_e = o3d_request.get('lon_e', None)
    output = o3d_request.get('output')
    output_dir = o3d_request.get('output_dir')
    
    TS_3dtrend_data = TS_3dtrend(data)
    TS_3dtrend_data.attrs = data.attrs
    data = TS_3dtrend_data

    data = weighted_zonal_mean(data, region, lat_s, lat_n, lon_w, lon_e)

    fig, (axs) = plt.subplots(nrows=1, ncols=2, figsize=(14, 5))

    data.avg_thetao.plot.contourf(levels=20, ax=axs[0])
    axs[0].set_ylim((5500, 0))

    region_title = custom_region(region=region, lat_s=lat_s, lat_n=lat_n,
                                 lon_w=lon_w, lon_e=lon_e)
    title = f"Zonally-averaged long-term trends in the {region_title}"
    fig.suptitle(title, fontsize=20)

    plt.subplots_adjust(top=0.85)

    axs[0].set_title("Temperature", fontsize=14)
    axs[0].set_ylabel("Depth (in m)", fontsize=9)
    axs[0].set_xlabel("Latitude (in deg North)", fontsize=9)
    axs[0].set_facecolor('grey')

    data.avg_so.plot.contourf(levels=20, ax=axs[1])
    axs[1].set_ylim((5500, 0))
    axs[1].set_title("Salinity", fontsize=14)
    axs[1].set_ylabel("Depth (in m)", fontsize=12)
    axs[1].set_xlabel("Latitude (in deg North)", fontsize=12)
    axs[1].set_facecolor('grey')

    if output:
        filename = file_naming(region, lat_s, lat_n, lon_w, lon_e, plot_name=f"{model}-{exp}-{source}_zonal_mean_trend")
        write_data(output_dir,filename, data)
        export_fig(output_dir, filename , "pdf", metadata_value = title, loglevel= loglevel)

    # plt.show()

    return


def reg_mean(data, region=None, lat_s=None, lat_n=None, lon_w=None, lon_e=None, loglevel= "WARNING"):
    """
    Computes the weighted box mean for some predefined or customized region

    Parameters:
        data (xarray.Dataset): Input data.

        region (str, optional): Predefined region name. If provided, latitude and longitude bounds will be fetched from predefined regions.

        lat_s (float, optional): Southern latitude bound. Required if region is not provided or None.

        lat_n (float, optional): Northern latitude bound. Required if region is not provided or None.

        lon_w (float, optional): Western longitude bound. Required if region is not provided or None.

        lon_e (float, optional): Eastern longitude bound. Required if region is not provided or None.

    Returns:
        xarray.Dataset: Standardised anomaly with respect to the initial time step of the input data.
    """
    logger = log_configure(loglevel, 'split_ocean3d_req')
    data = weighted_area_mean(data, region, lat_s, lat_n, lon_w, lon_e)

    return data

    
