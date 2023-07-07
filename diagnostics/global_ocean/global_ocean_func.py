import datetime
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import warnings, logging
from aqua.util import load_yaml

warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def predefined_regions(region):
    region = region.lower()
    if region in ["indian ocean", "indian_ocean"]:
        latN = 30.0
        latS = -30.0
        lonW = 100.0
        lonE = 300.0
    elif region in ["labrador sea"]:
        latN = 65.0
        latS = 50.0
        lonW = 300.0
        lonE = 325.0
    elif region in ["global ocean"]:
        latN = 90.0
        latS = -90.0
        lonW = 0.0
        lonE = 360.0
    elif region in ["atlantic ocean"]:
        latN = 65.0
        latS = -35.0
        lonW = -80.0
        lonE = 30.0
    elif region in ["pacific ocean"]:
        latN = 65.0
        latS = -55.0
        lonW = 120.0
        lonE = 290.0
    elif region in ["arctic ocean"]:
        latN = 90.0
        latS = 65.0
        lonW = 0.0
        lonE = 360.0
    elif region in ["southern ocean"]: 
        latN = -55.0
        latS = -80.0
        lonW = -180.0
        lonE = 180.0
    else:
        raise ValueError("Invalid region. Available options: 'Indian Ocean', 'Labrador Sea', 'Global Ocean', 'Atlantic Ocean', 'Pacific Ocean', 'Arctic Ocean', 'Southern Ocean'")
    return latS, latN, lonW, lonE

def convert_longitudes(data):
    # Shift longitudes from -180 to 180 range to 0 to 360 range
    data = data.assign_coords(lon=(((data["lon"] + 180) % 360) - 180))
    # Roll the data so that the prime meridian is at the center
    data = data.roll(lon=int(len(data['lon']) / 2), roll_coords=True)
    
    return data

def weighted_area_mean(data, region=None, latS: float=None, latN: float=None, lonW: float=None, lonE: float=None):
    """
    Compute the weighted area mean of data within the specified latitude and longitude bounds.

    Parameters:
        data (xarray.Dataset): Input data.
        
        region (str, optional): Predefined region name. If provided, latitude and longitude bounds will be fetched from predefined regions.
        
        latS (float, optional): Southern latitude bound. Required if region is not provided or None.
        
        latN (float, optional): Northern latitude bound. Required if region is not provided or None.
        
        lonW (float, optional): Western longitude bound. Required if region is not provided or None.
        
        lonE (float, optional): Eastern longitude bound. Required if region is not provided or None.

    Returns:
        xarray.Dataset: Weighted area mean of the input data.
    """
    if region is None:
        if latN is None or latS is None or lonW is None or lonE is None:
            raise ValueError("When region is None, latN, latS, lonW, lonE values need to be specified.")
        
        if lonW < 0 or lonE < 0:
            data = convert_longitudes(data)
    else:
        # Obtain latitude and longitude boundaries for the predefined region
        latS, latN, lonW, lonE = predefined_regions(region)
    logger.info(f" data slicing for this region, latitude {latS} to {latN}, longitude {lonW} to {lonE}")
    # Perform data slicing based on the specified or predefined latitude and longitude boundaries
    data = data.sel(lat=slice(latS, latN), lon=slice(lonW, lonE))
    # Calculate weighted data based on cosine of latitude
    weighted_data = data.weighted(np.cos(np.deg2rad(data.lat)))
    # Calculate weighted mean along latitude and longitude axes
    wgted_mean = weighted_data.mean(("lat", "lon"))
    
    return wgted_mean



def mean_value_plot(data, region, customise_level=False, levels=None, outputfig="./figs"):
    # Calculate weighted area mean
    data = weighted_area_mean(data, True, region)

    # Create subplots
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(14, 5))

    # Set the title
    fig.suptitle(region, fontsize=16)

    # Define the levels for plotting
    if customise_level:
        if levels is None:
            raise ValueError("Custom levels are selected, but levels are not provided.")
    else:
        levels = [0, 100, 500, 1000, 2000, 3000, 4000, 5000]

    # Plot data for each level
    for level in levels:
        if level != 0:
            data_level = data.sel(lev=slice(None, level)).isel(lev=-1)
        else:
            data_level = data.isel(lev=0)

        # Plot temperature
        data_level.ocpt.plot.line(ax=ax1,label=f"{round(int(data_level.lev.data), -2)}")

        # Plot salinity
        data_level.so.plot.line(ax=ax2,label=f"{round(int(data_level.lev.data), -2)}")

    # Set properties for the temperature subplot
    ax1.set_title("Temperature", fontsize=14)
    ax1.set_ylabel("Standardized Units (at the respective level)", fontsize=12)
    ax1.set_xlabel("Time (in years)", fontsize=12)
    ax1.legend(loc="best")

    # Set properties for the salinity subplot
    ax2.set_title("Salinity", fontsize=14)
    ax2.set_ylabel("Standardized Units (at the respective level)", fontsize=12)
    ax2.set_xlabel("Time (in years)", fontsize=12)
    ax2.legend(loc="best")
    filename = f"{outputfig}/TS_{region.replace(' ', '_').lower()}_mean.png"

    plt.savefig(filename)
    logger.info(f"{filename} saved")
    # Adjust the layout and display the plot
    plt.show()

    # Return the last value of data_level
    return 




def std_anom_wrt_initial(data, region=None, latS=None, latN=None, lonW=None, lonE=None):
    """
    Compute the standard anomaly with respect to the initial time step of data within the specified latitude and longitude bounds.
    Normalization is done with respect to the standard deviation of the respective vertical level

    Parameters:
        data (xarray.Dataset): Input data.
        
        region (str, optional): Predefined region name. If provided, latitude and longitude bounds will be fetched from predefined regions.
        
        latS (float, optional): Southern latitude bound. Required if region is not provided or None.
        
        latN (float, optional): Northern latitude bound. Required if region is not provided or None.
        
        lonW (float, optional): Western longitude bound. Required if region is not provided or None.
        
        lonE (float, optional): Eastern longitude bound. Required if region is not provided or None.

    Returns:
        xarray.Dataset: Standardised anomaly with respect to the initial time step of the input data.
    """

    std_anomaly = xr.Dataset()

    # Compute the weighted area mean over the specified latitude and longitude range
    wgted_mean = weighted_area_mean(data, region, latS, latN, lonW, lonE)

    # Calculate the anomaly from the initial time step for each variable
    for var in list(data.data_vars.keys()):
        anomaly_from_initial = wgted_mean[var] - wgted_mean[var].isel(time=0)
        
        # Calculate the standard anomaly by dividing the anomaly by its standard deviation along the time dimension
        std_anomaly[var] = anomaly_from_initial / anomaly_from_initial.std(dim="time")

    return std_anomaly

def reg_mean(data, region=None, latS=None, latN=None, lonW=None, lonE=None):
    """
    Computes the weighted box mean for some predefined or customized region

    Parameters:
        data (xarray.Dataset): Input data.
        
        region (str, optional): Predefined region name. If provided, latitude and longitude bounds will be fetched from predefined regions.
        
        latS (float, optional): Southern latitude bound. Required if region is not provided or None.
        
        latN (float, optional): Northern latitude bound. Required if region is not provided or None.
        
        lonW (float, optional): Western longitude bound. Required if region is not provided or None.
        
        lonE (float, optional): Eastern longitude bound. Required if region is not provided or None.

    Returns:
        xarray.Dataset: Standardised anomaly with respect to the initial time step of the input data.
    """

    reg_mean = xr.Dataset()

    # Compute the weighted area mean over the specified latitude and longitude range
    reg_mean = weighted_area_mean(data, region, latS, latN, lonW, lonE)


    return reg_mean

def anom_wrt_initial(data, region=None, latS=None, latN=None, lonW=None, lonE=None):
    """
    Compute the anomaly with respect to the initial time step of data within the specified latitude and longitude bounds.

    Parameters:
        data (xarray.Dataset): Input data.
        
        region (str, optional): Predefined region name. If provided, latitude and longitude bounds will be fetched from predefined regions.
        
        latS (float, optional): Southern latitude bound. Required if region is not provided or None.
        
        latN (float, optional): Northern latitude bound. Required if region is not provided or None.
        
        lonW (float, optional): Western longitude bound. Required if region is not provided or None.
        
        lonE (float, optional): Eastern longitude bound. Required if region is not provided or None.

    Returns:
        xarray.Dataset: Standard anomaly with respect to the initial time step of the input data.
    """

    anomaly = xr.Dataset()

    # Compute the weighted area mean over the specified latitude and longitude range
    wgted_mean = weighted_area_mean(data, region, latS, latN, lonW, lonE)

    # Calculate the anomaly from the initial time step for each variable
    for var in list(data.data_vars.keys()):
        anomaly[var] = wgted_mean[var] - wgted_mean[var].isel(time=0)
    return anomaly


def std_anom_wrt_time_mean(data, region=None, latS=None, latN=None, lonW=None, lonE=None):
    """
    Compute the standardised anomaly with respect to the time mean of data within the specified latitude and longitude bounds.
    Normalization is done with respect to the standard deviation of the respective vertical level
   
    Parameters:
        data (xarray.Dataset): Input data.
        
        region (str, optional): Predefined region name. If provided, latitude and longitude bounds will be fetched from predefined regions.
        
        latS (float, optional): Southern latitude bound. Required if region is not provided or None.
        
        latN (float, optional): Northern latitude bound. Required if region is not provided or None.
        
        lonW (float, optional): Western longitude bound. Required if region is not provided or None.
        
        lonE (float, optional): Eastern longitude bound. Required if region is not provided or None.

    Returns:
        xarray.Dataset: Standardised anomaly with respect to the time mean of the input data.
    """
    # Create an empty dataset to store the results
    std_anomaly = xr.Dataset()

    # Compute the weighted area mean over the specified latitude and longitude range
    wgted_mean = weighted_area_mean(data, region, latS, latN, lonW, lonE)

    # Calculate the anomaly from the time mean for each variable
    for var in list(data.data_vars.keys()):
        anomaly_from_time_mean = wgted_mean[var] - wgted_mean[var].mean("time")
        
        # Calculate the standard anomaly by dividing the anomaly by its standard deviation along the time dimension
        std_anomaly[var] = anomaly_from_time_mean / anomaly_from_time_mean.std("time")

    return std_anomaly

def ocpt_so_anom_plot(data, region, outputfig="./figs"):
    """
    Create a Hovmoller plot of temperature and salinity anomalies.

    Args:
        data (DataArray): Input data containing temperature (ocpt) and salinity (so).
        title (str): Title of the plot.

    Returns:
        None
    """
    # Create subplots for temperature and salinity plots
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(14, 5))
    fig.suptitle(f"Standardised {region} T,S Anomalies (wrt first value)", fontsize=16)

    # Extract temperature data and plot the contour filled plot
    tgt = data.ocpt.transpose()
    tgt.plot.contourf(levels=12, ax=ax1)

    # Add contour lines with black color and set the line width
    tgt.plot.contour(colors="black", levels=12, linewidths=0.5, ax=ax1)

    # Set the title, y-axis label, and x-axis label for the temperature plot
    ax1.set_title("Temperature", fontsize=14)
    ax1.set_ylim((5500, 0))
    ax1.set_ylabel("Depth (in m)", fontsize=12)
    ax1.set_xlabel("Time (in years)", fontsize=12)

    # Extract salinity data and plot the contour filled plot
    sgt = data.so.transpose()
    sgt.plot.contourf(levels=12, ax=ax2)

    # Add contour lines with black color and set the line width
    sgt.plot.contour(colors="black", levels=12, linewidths=0.5, ax=ax2)

    # Set the title, y-axis label, and x-axis label for the salinity plot
    ax2.set_title("Salinity", fontsize=14)
    ax2.set_ylim((5500, 0))
    ax2.set_ylabel("Depth (in m)", fontsize=12)
    ax2.set_xlabel("Time (in years)", fontsize=12)
    filename = f"{outputfig}/TS_anomalies_{region.replace(' ', '_').lower()}.png"
    plt.savefig(filename)
    logger.info(f"{filename} saved")
    # Return the plot
    return

def ocpt_so_std_plot(data, region, outputfig="./figs"):
    """
    Create a Hovmoller plot of temperature and salinity standardised anomalies.

    Args:
        data (DataArray): Input data containing temperature (ocpt) and salinity (so).
        title (str): Title of the plot.

    Returns:
        None
    """
    # Create subplots for temperature and salinity plots
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(14, 5))
    fig.suptitle(f"Standardised {region} T,S Anomalies (wrt first value)", fontsize=16)

    # Extract temperature data and plot the contour filled plot
    tgt = data.ocpt.transpose()
    tgt.plot.contourf(levels=12, ax=ax1)

    # Add contour lines with black color and set the line width
    tgt.plot.contour(colors="black", levels=12, linewidths=0.5, ax=ax1)

    # Set the title, y-axis label, and x-axis label for the temperature plot
    ax1.set_title("Temperature", fontsize=14)
    ax1.set_ylim((5500, 0))
    ax1.set_ylabel("Depth (in m)", fontsize=12)
    ax1.set_xlabel("Time (in years)", fontsize=12)

    # Extract salinity data and plot the contour filled plot
    sgt = data.so.transpose()
    sgt.plot.contourf(levels=12, ax=ax2)

    # Add contour lines with black color and set the line width
    sgt.plot.contour(colors="black", levels=12, linewidths=0.5, ax=ax2)

    # Set the title, y-axis label, and x-axis label for the salinity plot
    ax2.set_title("Salinity", fontsize=14)
    ax2.set_ylim((5500, 0))
    ax2.set_ylabel("Depth (in m)", fontsize=12)
    ax2.set_xlabel("Time (in years)", fontsize=12)
    filename = f"{outputfig}/TS_anomalies_{region.replace(' ', '_').lower()}.png"
    plt.savefig(filename)
    logger.info(f"{filename} saved")
    # Return the plot
    return

def ocpt_so_full_plot(data, region, outputfig="./figs"):
    """
    Create a Hovmoller plot of temperature and salinity full values.

    Args:
        data (DataArray): Input data containing temperature (ocpt) and salinity (so).
        title (str): Title of the plot.

    Returns:
        None
    """
    # Create subplots for temperature and salinity plots
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(14, 5))
    fig.suptitle(f"Full {region} T,S values", fontsize=16)

    # Extract temperature data and plot the contour filled plot
    tgt = data.ocpt.transpose()
    tgt.plot.contourf(levels=12, ax=ax1)

    # Add contour lines with black color and set the line width
    tgt.plot.contour(colors="black", levels=12, linewidths=0.5, ax=ax1)

    # Set the title, y-axis label, and x-axis label for the temperature plot
    ax1.set_title("Temperature", fontsize=14)
    ax1.set_ylim((5500, 0))
    ax1.set_ylabel("Depth (in m)", fontsize=12)
    ax1.set_xlabel("Time (in years)", fontsize=12)

    # Extract salinity data and plot the contour filled plot
    sgt = data.so.transpose()
    sgt.plot.contourf(levels=12, ax=ax2)

    # Add contour lines with black color and set the line width
    sgt.plot.contour(colors="black", levels=12, linewidths=0.5, ax=ax2)

    # Set the title, y-axis label, and x-axis label for the salinity plot
    ax2.set_title("Salinity", fontsize=14)
    ax2.set_ylim((5500, 0))
    ax2.set_ylabel("Depth (in m)", fontsize=12)
    ax2.set_xlabel("Time (in years)", fontsize=12)
    filename = f"{outputfig}/TS_anomalies_{region.replace(' ', '_').lower()}.png"
    plt.savefig(filename)
    logger.info(f"{filename} saved")
    # Return the plot
    return

def ocpt_so_hov_plot(data, region, type, outputfig="./figs"):
    """
    Create a Hovmoller plot of temperature and salinity full values.

    Args:
        data (DataArray): Input data containing temperature (ocpt) and salinity (so).
        region (str): Region that is represented in the plot.
        type (str): Type of timeseries between FullValue, Anomaly, StdAnomaly


    Returns:
        None
    """
    # Reads the type of timeseries to plot

    if type is None:
        raise ValueError("Please specify whether it is a 'FullValue', 'Anomaly' or 'StdAnomaly' timeseries")
    elif type == 'FullValue':
        ttype="Full Values"
    elif type == 'Anomaly':
        ttype="Anomalies"
    elif type == 'StdAnomaly':
        data.ocpt.attrs['units'] = 'Standardised Units'
        data.so.attrs['units'] = 'Standardised Units'
        ttype="Standardised Anomalies"

    # Create subplots for temperature and salinity plots
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(14, 5))
    fig.suptitle(f"{type} {region} T,S evolution", fontsize=16)

    # Extract temperature data and plot the contour filled plot
    tgt = data.ocpt.transpose()
    tgt.plot.contourf(levels=12, ax=ax1)

    # Add contour lines with black color and set the line width
    tgt.plot.contour(colors="black", levels=12, linewidths=0.5, ax=ax1)

    # Set the title, y-axis label, and x-axis label for the temperature plot
    ax1.set_title("Temperature", fontsize=14)
    ax1.set_ylim((5500, 0))
    ax1.set_ylabel("Depth (in m)", fontsize=12)
    ax1.set_xlabel("Time (in years)", fontsize=12)

    # Extract salinity data and plot the contour filled plot
    sgt = data.so.transpose()
    sgt.plot.contourf(levels=12, ax=ax2)

    # Add contour lines with black color and set the line width
    sgt.plot.contour(colors="black", levels=12, linewidths=0.5, ax=ax2)

    # Set the title, y-axis label, and x-axis label for the salinity plot
    ax2.set_title("Salinity", fontsize=14)
    ax2.set_ylim((5500, 0))
    ax2.set_ylabel("Depth (in m)", fontsize=12)
    ax2.set_xlabel("Time (in years)", fontsize=12)

    filename = f"{outputfig}/Hovmoller_TS_{type.replace(' ', '_')}_{region.replace(' ', '_').lower()}.png"
    plt.savefig(filename)
    logger.info(f"{filename} saved")
    # Return the plot
    return

def time_series(data, region, customise_level=False, levels=None, outputfig="./figs"):
    """
    Create time series plots of global temperature and salinity standardised anomalies at selected levels.

    Args:
        data (DataArray): Input data containing temperature (ocpt) and salinity (so).
        region (str): Region name.
        customise_level (bool): Whether to use custom levels or predefined levels.
        levels (list): List of levels to plot. Ignored if customise_level is False.

    Returns:
        None
    """
    # Create subplots for temperature and salinity time series plots
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(14, 5))

    fig.suptitle(f"Standardised {region} T,S Anomalies (wrt first value)", fontsize=16)

    # Define the levels at which to plot the time series
    if customise_level:
        if levels is None:
            raise ValueError("Custom levels are selected, but levels are not provided.")
    else:
        levels = [0, 100, 500, 1000, 2000, 3000, 4000, 5000]

    # Iterate over the levels and plot the time series for each level
    for level in levels:
        if level != 0:
            # Select the data at the specified level
            data_level = data.sel(lev=slice(None, level)).isel(lev=-1)
        else:
            # Select the data at the surface level (0)
            data_level = data.isel(lev=0)
        # Plot the temperature time series
        data_level.ocpt.plot.line(ax=ax1,label=f"{round(int(data_level.lev.data), -2)}")

        # Plot the salinity time series
        data_level.so.plot.line(ax=ax2,label=f"{round(int(data_level.lev.data), -2)}")

    # Set the title, y-axis label, and x-axis label for the temperature plot
    ax1.set_title("Temperature", fontsize=14)
    ax1.set_ylabel("Standardised Units (at the respective level)", fontsize=12)
    ax1.set_xlabel("Time (in years)", fontsize=12)
    ax1.legend(loc='best')

    # Set the title, y-axis label, and x-axis label for the salinity plot
    ax2.set_title("Salinity", fontsize=14)
    ax2.set_ylabel("Standardised Units (at the respective level)", fontsize=12)
    ax2.set_xlabel("Time (in years)", fontsize=12)
    ax2.legend(loc='best')
    filename = f"{outputfig}/TS_time_series_anomalies_{region.replace(' ', '_').lower()}.png"

    plt.savefig(filename)
    logger.info(f"{filename} saved")
    plt.show()

    # Return the plot
    return

def time_series_custom(data, region, type,customise_level=False, levels=None, outputfig="./figs"):
    """
    Create time series plots of global temperature and salinity standardised anomalies at selected levels.

    Args:
        data (DataArray): Input data containing temperature (ocpt) and salinity (so).
        region (str): Region name.
        customise_level (bool): Whether to use custom levels or predefined levels.
        levels (list): List of levels to plot. Ignored if customise_level is False.
        type (str): Type of timeseries between FullValue, Anomaly, StdAnomaly

    Returns:
        None
    """
    # Create subplots for temperature and salinity time series plots
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(14, 5))


    # Reads the type of timeseries to plot

    if type is None:
        raise ValueError("Please specify whether it is a 'FullValue', 'Anomaly' or 'StdAnomaly' timeseries")
    elif type == 'FullValue':
        ylabT="Potential Temperature (in °C)"
        ylabS="Practical Salinity (in psu)"
        ttype="Full Values"
    elif type == 'Anomaly':
        ylabT="Potential Temperature Anomaly (in °C)"
        ylabS="Practical Salinity Anomaly(in psu)"
        ttype="Anomalies"
    elif type == 'StdAnomaly':
        ylabT="Standardised Units"
        ylabS="Standardised Units"
        ttype="Standardised Anomalies"

    

    # Define the levels at which to plot the time series
    if customise_level:
        if levels is None:
            raise ValueError("Custom levels are selected, but levels are not provided.")
    else:
        levels = [0, 100, 500, 1000, 2000, 3000, 4000, 5000]

    # Iterate over the levels and plot the time series for each level
    for level in levels:
        if level != 0:
            # Select the data at the specified level
            data_level = data.sel(lev=slice(None, level)).isel(lev=-1)
        else:
            # Select the data at the surface level (0)
            data_level = data.isel(lev=0)
        # Plot the temperature time series
        data_level.ocpt.plot.line(ax=ax1,label=f"{round(int(data_level.lev.data), -2)}")

        # Plot the salinity time series
        data_level.so.plot.line(ax=ax2,label=f"{round(int(data_level.lev.data), -2)}")

    fig.suptitle(f"Spatially-averaged {region} T,S {ttype}", fontsize=16)


    # Set the title, y-axis label, and x-axis label for the temperature plot
    ax1.set_title("Temperature", fontsize=14)
    ax1.set_ylabel(ylabT, fontsize=12)
    ax1.set_xlabel("Time (in years)", fontsize=12)
    ax1.legend(loc='best')

    # Set the title, y-axis label, and x-axis label for the salinity plot
    ax2.set_title("Salinity", fontsize=14)
    ax2.set_ylabel(ylabS, fontsize=12)
    ax2.set_xlabel("Time (in years)", fontsize=12)
    ax2.legend(loc='best')
    filename = f"{outputfig}/TS_time_series_{type.replace(' ', '_').lower()}_{region.replace(' ', '_').lower()}.png"

    plt.savefig(filename)
    logger.info(f"{filename} saved")
    plt.show()

    # Return the plot
    return


def convert_so(so):
    """
    Convert practical salinity to absolute.

    Parameters
    ----------
    so: dask.array.core.Array
        Masked array containing the practical salinity values (psu or 0.001).

    Returns
    -------
    absso: dask.array.core.Array
        Masked array containing the absolute salinity values (g/kg).

    Note
    ----
    This function use an approximation from TEOS-10 equations and could
    lead to different values in particular in the Baltic Seas.
    http://www.teos-10.org/pubs/gsw/pdf/SA_from_SP.pdf

    """
    return so / 0.99530670233846


def convert_ocpt(absso, ocpt):
    """
    convert potential temperature to conservative temperature
    
    Parameters
    ----------
    absso: dask.array.core.Array
        Masked array containing the absolute salinity values.
    ocpt: dask.array.core.Array
        Masked array containing the potential temperature values (degC).

    Returns
    -------
    bigocpt: dask.array.core.Array
        Masked array containing the conservative temperature values (degC).

    Note
    ----
    http://www.teos-10.org/pubs/gsw/html/gsw_CT_from_pt.html

    """
    x = np.sqrt(0.0248826675584615*absso)
    y = ocpt*0.025e0
    enthalpy = 61.01362420681071e0 + y*(168776.46138048015e0 +
        y*(-2735.2785605119625e0 + y*(2574.2164453821433e0 +
        y*(-1536.6644434977543e0 + y*(545.7340497931629e0 +
        (-50.91091728474331e0 - 18.30489878927802e0*y)*
        y))))) + x**2*(268.5520265845071e0 + y*(-12019.028203559312e0 +
        y*(3734.858026725145e0 + y*(-2046.7671145057618e0 +
        y*(465.28655623826234e0 + (-0.6370820302376359e0 -
        10.650848542359153e0*y)*y)))) +
        x*(937.2099110620707e0 + y*(588.1802812170108e0+
        y*(248.39476522971285e0 + (-3.871557904936333e0-
        2.6268019854268356e0*y)*y)) +
        x*(-1687.914374187449e0 + x*(246.9598888781377e0 +
        x*(123.59576582457964e0 - 48.5891069025409e0*x)) +
        y*(936.3206544460336e0 +
        y*(-942.7827304544439e0 + y*(369.4389437509002e0 +
        (-33.83664947895248e0 - 9.987880382780322e0*y)*y))))))

    return enthalpy/3991.86795711963


def compute_rho(absso, bigocpt, ref_pressure):
    """
    Computes the potential density in-situ.

    Parameters
    ----------
    absso: dask.array.core.Array
        Masked array containing the absolute salinity values (g/kg).
    bigocpt: dask.array.core.Array
        Masked array containing the conservative temperature values (degC).
    ref_pressure: float
        Reference pressure (dbar).

    Returns
    -------
    rho: dask.array.core.Array
        Masked array containing the potential density in-situ values (kg m-3).

    Note
    ----
    https://github.com/fabien-roquet/polyTEOS/blob/36b9aef6cd2755823b5d3a7349cfe64a6823a73e/polyTEOS10.py#L57

    """
    # reduced variables
    SAu = 40.*35.16504/35.
    CTu = 40.
    Zu = 1e4
    deltaS = 32.
    ss = np.sqrt((absso+deltaS)/SAu)
    tt = bigocpt / CTu
    pp = ref_pressure / Zu

    # vertical reference profile of density
    R00 = 4.6494977072e+01
    R01 = -5.2099962525e+00
    R02 = 2.2601900708e-01
    R03 = 6.4326772569e-02
    R04 = 1.5616995503e-02
    R05 = -1.7243708991e-03
    r0 = (((((R05*pp + R04)*pp + R03)*pp + R02)*pp + R01)*pp + R00)*pp

    # density anomaly
    R000 = 8.0189615746e+02
    R100 = 8.6672408165e+02
    R200 = -1.7864682637e+03
    R300 = 2.0375295546e+03
    R400 = -1.2849161071e+03
    R500 = 4.3227585684e+02
    R600 = -6.0579916612e+01
    R010 = 2.6010145068e+01
    R110 = -6.5281885265e+01
    R210 = 8.1770425108e+01
    R310 = -5.6888046321e+01
    R410 = 1.7681814114e+01
    R510 = -1.9193502195e+00
    R020 = -3.7074170417e+01
    R120 = 6.1548258127e+01
    R220 = -6.0362551501e+01
    R320 = 2.9130021253e+01
    R420 = -5.4723692739e+00
    R030 = 2.1661789529e+01
    R130 = -3.3449108469e+01
    R230 = 1.9717078466e+01
    R330 = -3.1742946532e+00
    R040 = -8.3627885467e+00
    R140 = 1.1311538584e+01
    R240 = -5.3563304045e+00
    R050 = 5.4048723791e-01
    R150 = 4.8169980163e-01
    R060 = -1.9083568888e-01
    R001 = 1.9681925209e+01
    R101 = -4.2549998214e+01
    R201 = 5.0774768218e+01
    R301 = -3.0938076334e+01
    R401 = 6.6051753097e+00
    R011 = -1.3336301113e+01
    R111 = -4.4870114575e+00
    R211 = 5.0042598061e+00
    R311 = -6.5399043664e-01
    R021 = 6.7080479603e+0
    R121 = 3.5063081279e+00
    R221 = -1.8795372996e+00
    R031 = -2.4649669534e+00
    R131 = -5.5077101279e-01
    R041 = 5.5927935970e-01
    R002 = 2.0660924175e+00
    R102 = -4.9527603989e+00
    R202 = 2.5019633244e+00
    R012 = 2.0564311499e+00
    R112 = -2.1311365518e-01
    R022 = -1.2419983026e+00
    R003 = -2.3342758797e-02
    R103 = -1.8507636718e-02
    R013 = 3.7969820455e-01

    rz3 = R013*tt + R103*ss + R003
    rz2 = (R022*tt+R112*ss+R012)*tt+(R202*ss+R102)*ss+R002
    rz1 = (((R041*tt+R131*ss+R031)*tt +
            (R221*ss+R121)*ss+R021)*tt +
           ((R311*ss+R211)*ss+R111)*ss+R011)*tt + \
        (((R401*ss+R301)*ss+R201)*ss+R101)*ss+R001
    rz0 = (((((R060*tt+R150*ss+R050)*tt +
              (R240*ss+R140)*ss+R040)*tt +
             ((R330*ss+R230)*ss+R130)*ss+R030)*tt +
            (((R420*ss+R320)*ss+R220)*ss+R120)*ss+R020)*tt +
           ((((R510*ss+R410)*ss+R310)*ss+R210)*ss+R110)*ss+R010)*tt + \
        (((((R600*ss+R500)*ss+R400)*ss+R300)*ss+R200)*ss+R100)*ss+R000
    r = ((rz3*pp + rz2)*pp + rz1)*pp + rz0

    # in-situ density
    return r + r0


    
def convert_variables(data):
    """
    Convert variables in the given dataset to absolute salinity, conservative temperature, and potential density.

    Parameters
    ----------
    data : xarray.Dataset
        Dataset containing the variables to be converted.

    Returns
    -------
    converted_data : xarray.Dataset
        Dataset containing the converted variables: absolute salinity (so), conservative temperature (ocpt),
        and potential density (rho) at reference pressure 0 dbar.

    """
    converted_data = xr.Dataset()

    # Convert practical salinity to absolute salinity
    absso = convert_so(data.so)

    # Convert potential temperature to conservative temperature
    ocpt = convert_ocpt(absso, data.ocpt)

    # Compute potential density in-situ at reference pressure 0 dbar
    rho = compute_rho(absso, ocpt, 0)

    # Merge the converted variables into a new dataset
    converted_data = converted_data.merge({"so": absso, "ocpt": ocpt, "rho": rho})

    return converted_data




def plot_temporal_split(data, area_name, outputfig="./figs"):
    """
    Plot temporal split of mean state annual temperature, salinity, and density stratification.

    Parameters
    ----------
    data : xarray.Dataset
        Dataset containing the data for temperature (ocpt), salinity (so), and density (rho).
    area_name : str
        Name of the area for the plot title.

    Returns
    -------
    None

    """
    date_len = len(data.time)
    if date_len != 1:
        if date_len % 2 == 0:
            data_1 = data.isel(time=slice(0, int(date_len/2)))
            data_2 = data.isel(time=slice(int(date_len/2), date_len))
        else:
            data_1 = data.isel(time=slice(0, int((date_len-1)/2)))
            data_2 = data.isel(time=slice(int((date_len-1)/2), date_len))

    fig, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3, figsize=(14, 8))
    fig.suptitle(f"Mean state annual T, S, rho0 stratification in {area_name}", fontsize=16)

    ax1.set_ylim((4500, 0))
    ax1.plot(data_1.ocpt.mean("time"), data.lev, 'g-', linewidth=2.0)
    ax1.plot(data_2.ocpt.mean("time"), data.lev, 'b-', linewidth=2.0)
    ax1.set_title("Temperature Profile", fontsize=14)
    ax1.set_ylabel("Depth (m)", fontsize=12)
    ax1.set_xlabel("Temperature (°C)", fontsize=12)
    ax1.legend([f"EXP first half {data_1.time[0].dt.year.data}-{data_1.time[-1].dt.year.data}",
                f"EXP last half {data_2.time[0].dt.year.data}-{data_2.time[-1].dt.year.data}",
                "EN4 1950-1980", "EN4 1990-2020"], loc='best')

    ax2.set_ylim((4500, 0))
    ax2.plot(data_1.so.mean("time"), data.lev, 'g-', linewidth=2.0)
    ax2.plot(data_2.so.mean("time"), data.lev, 'b-', linewidth=2.0)
    ax2.set_title("Salinity Profile", fontsize=14)
    ax2.set_xlabel("Salinity (psu)", fontsize=12)

    ax3.set_ylim((4500, 0))
    ax3.plot(data_1.rho.mean("time")-1000, data.lev, 'g-', linewidth=2.0)
    ax3.plot(data_2.rho.mean("time")-1000, data.lev, 'b-', linewidth=2.0)
    ax3.set_title("Rho (ref 0) Profile", fontsize=14)
    ax3.set_xlabel("Density Anomaly (kg/m³)", fontsize=12)
    
    filename = f"{outputfig}/vertical_TS_{area_name.replace(' ', '_').lower()}_mean.png"

    plt.savefig(filename)
    logger.info(f"{filename} saved")

    plt.show()


def linregress_3D(y_array):
    """
    Computes the linear regression against the temporal dimension of a 3D array formated in time, latitude and longitude

    The function was copied from https://stackoverflow.com/questions/52108417/how-to-apply-linear-regression-to-every-pixel-in-a-large-multi-dimensional-array
    and is a very efficient way to compute trends in 3D arrays

    The drawback is that it returns the coefficients in a simple array, not as xarray, but this can be corrected with the
    companion function array2xarray

    Parameters
    ----------
    data : y_array.Dataset
    
    Dataset containing a single 3D field with time, latitude and longitude as coordinates
 

    Returns
    -------
    n,slope,intercept,p_val,r_square,rmse

    """
    
    x_array=np.empty(y_array.shape)
    for i in range(y_array.shape[0]): x_array[i,:,:]=i+1 # This would be fine if time series is not too long. Or we can use i+yr (e.g. 2019).
    x_array[np.isnan(y_array)]=np.nan
    # Compute the number of non-nan over each (lon,lat) grid box.
    n=np.sum(~np.isnan(x_array),axis=0)
    # Compute mean and standard deviation of time series of x_array and y_array over each (lon,lat) grid box.
    x_mean=np.nanmean(x_array,axis=0)
    y_mean=np.nanmean(y_array,axis=0)
    x_std=np.nanstd(x_array,axis=0)
    y_std=np.nanstd(y_array,axis=0)
    # Compute co-variance between time series of x_array and y_array over each (lon,lat) grid box.
    cov=np.nansum((x_array-x_mean)*(y_array-y_mean),axis=0)/n
    # Compute correlation coefficients between time series of x_array and y_array over each (lon,lat) grid box.
    cor=cov/(x_std*y_std)
    # Compute slope between time series of x_array and y_array over each (lon,lat) grid box.
    slope=cov/(x_std**2)
    # Compute intercept between time series of x_array and y_array over each (lon,lat) grid box.
    intercept=y_mean-x_mean*slope
    # Compute tstats, stderr, and p_val between time series of x_array and y_array over each (lon,lat) grid box.
    tstats=cor*np.sqrt(n-2)/np.sqrt(1-cor**2)
    stderr=slope/tstats
    from scipy.stats import t
    p_val=t.sf(tstats,n-2)*2
    # Compute r_square and rmse between time series of x_array and y_array over each (lon,lat) grid box.
    # r_square also equals to cor**2 in 1-variable lineare regression analysis, which can be used for checking.
    r_square=np.nansum((slope*x_array+intercept-y_mean)**2,axis=0)/np.nansum((y_array-y_mean)**2,axis=0)
    rmse=np.sqrt(np.nansum((y_array-slope*x_array-intercept)**2,axis=0)/n)
    # Do further filteration if needed (e.g. We stipulate at least 3 data records are needed to do regression analysis) and return values
    n=n*1.0 # convert n from integer to float to enable later use of np.nan
    n[n<3]=np.nan
    slope[np.isnan(n)]=np.nan
    intercept[np.isnan(n)]=np.nan
    p_val[np.isnan(n)]=np.nan
    r_square[np.isnan(n)]=np.nan
    rmse[np.isnan(n)]=np.nan
    return n,slope,intercept,p_val,r_square,rmse
  
def array2xarray(array,y_array):
    """
    Provides the longitudinal and latitudinal information of a given xarray to a simple array (to be used after linregress_3D)

    Parameters
    ----------
    array : input array Dataset
    
    y_array:  xarray Dataset with target coordinate information 

    Returns
    -------
    xarray

    """
    xarray=xr.DataArray(array,coords={"lat": y_array.lat,"lon": y_array.lon},name=str(y_array.name),dims=["lat","lon"])
    
    return xarray


def lintrend_2D(y_array):
    """
    Simplified version of linregress_3D that computes the trends in a 3D array formated in time, latitude and longitude coordinates

    It outputs the trends in xarray format

    Parameters
    ----------
    data : y_array.Dataset
    
    Dataset containing a single 3D field with time, latitude and longitude as coordinates
 

    Returns
    -------
    n,slope,intercept,p_val,r_square,rmse

    """
    
    x_array=np.empty(y_array.shape)
    for i in range(y_array.shape[0]): x_array[i,:,:]=i+1 # This would be fine if time series is not too long. Or we can use i+yr (e.g. 2019).
    x_array[np.isnan(y_array)]=np.nan
    # Compute the number of non-nan over each (lon,lat) grid box.
    n=np.sum(~np.isnan(x_array),axis=0)
    # Compute mean and standard deviation of time series of x_array and y_array over each (lon,lat) grid box.
    x_mean=np.nanmean(x_array,axis=0)
    y_mean=np.nanmean(y_array,axis=0)
    x_std=np.nanstd(x_array,axis=0)
    y_std=np.nanstd(y_array,axis=0)
    # Compute co-variance between time series of x_array and y_array over each (lon,lat) grid box.
    cov=np.nansum((x_array-x_mean)*(y_array-y_mean),axis=0)/n
    # Compute correlation coefficients between time series of x_array and y_array over each (lon,lat) grid box.
    cor=cov/(x_std*y_std)
    # Compute slope between time series of x_array and y_array over each (lon,lat) grid box.
    trend=cov/(x_std**2)
    
    # Do further filteration if needed (e.g. We stipulate at least 3 data records are needed to do regression analysis) and return values
    n=n*1.0 # convert n from integer to float to enable later use of np.nan
    n[n<3]=np.nan
    trend[np.isnan(n)]=np.nan
    
    #trend=xr.DataArray(trend,coords={"lat": y_array.lat,"lon": y_array.lon},name=str(y_array.name),dims=["lat","lon"])
    trend=xr.DataArray(trend,coords={"lat": y_array.lat,"lon": y_array.lon},name=f"{y_array.name} trends",dims=["lat","lon"])
    trend.attrs['units'] = f"{y_array.units}/year"

    #data.ocpt.attrs['units'] = 'Standardised Units'
    return trend

