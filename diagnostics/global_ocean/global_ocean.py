"""
Global Ocean module
"""

import datetime, os
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import warnings, logging
from aqua.util import load_yaml
from aqua import Reader,catalogue, inspect_catalogue

warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def predefined_regions(region):
    """
    Get the predefined latitude and longitude boundaries for a given region.

    Args:
        region (str): Name of the region.

    Returns:
        float, float, float, float: Latitude and longitude boundaries (latS, latN, lonW, lonE) for the region.

    Raises:
        ValueError: If an invalid region is provided.

    Available predefined regions:
    - 'Indian Ocean'
    - 'Labrador Sea'
    - 'Global Ocean'
    - 'Atlantic Ocean'
    - 'Pacific Ocean'
    - 'Arctic Ocean'
    - 'Southern Ocean'
    """
    region = region.lower().replace(" ","").replace("_","")
    if region in ["indianocean", "indian ocean"]:
        latN, latS, lonW, lonE = 30.0, -30.0, 30 ,110.0
    elif region in ["labradorsea", "labrador sea"]:
        latN, latS, lonW, lonE = 65.0, 50.0, 300.0, 325.0
    elif region in ["globalocean", "global ocean"]:
        latN, latS, lonW, lonE = 90.0, -90.0, 0.0, 360.0
    elif region in ["atlanticocean", "atlantic ocean"]:
        latN, latS, lonW, lonE = 65.0, -35.0, -80.0, 30.0
    elif region in ["pacificocean", "pacific ocean"]:
        latN, latS, lonW, lonE = 65.0, -55.0, 120.0, 290.0
    elif region in ["arcticocean", "arctic ocean"]:
        latN, latS, lonW, lonE = 90.0, 65.0, 0.0, 360.0
    elif region in ["southernocean", "southern ocean"]:
        latN, latS, lonW, lonE = -55.0, -80.0, -180.0, 180.0
    elif region in ["beringsea", "bering sea"]:
        latN, latS, lonW, lonE = 66.0, 53.0, 168.0, -178.0
    elif region in ["gulfofmexico", "gulf of mexico"]:
        latN, latS, lonW, lonE = 30.0, 18.0, -97.0, -81.0
    elif region in ["hudsonbay", "hudson bay"]:
        latN, latS, lonW, lonE = 63.0, 51.0, -95.0, -75.0
    elif region in ["redsea", "red sea"]:
        latN, latS, lonW, lonE = 30.0, 12.0, 32.0, 44.0
    elif region in ["persiangulf", "persian gulf"]:
        latN, latS, lonW, lonE = 30.0, 24.0, 48.0, 56.0
    elif region in ["adriaticsea", "adriatic sea"]:
        latN, latS, lonW, lonE = 45.0, 40.0, 13.0, 19.0
    elif region in ["caribbeansea", "caribbean sea"]:
        latN, latS, lonW, lonE = 23.0, 9.0, -85.0, -60.0
    elif region in ["seaofjapan", "sea of japan"]:
        latN, latS, lonW, lonE = 43.0, 34.0, 129.0, 132.0
    elif region in ["mediterraneansea", "mediterranean sea"]:
        latN, latS, lonW, lonE = 46.0, 30.0, -6.0, 36.0
    elif region in ["blacksea", "black sea"]:
        latN, latS, lonW, lonE = 45.0, 41.0, 27.0, 41.0
    elif region in ["southchina_sea", "south china sea"]:
        latN, latS, lonW, lonE = 21.0, 3.0, 99.0, 121.0
    elif region in ["arabiansea", "arabian sea"]:
        latN, latS, lonW, lonE = 25.0, 12.0, 50.0, 70.0
    elif region in ["coralsea", "coral sea"]:
        latN, latS, lonW, lonE = -10.0, -24.0, 147.0, 157.0
    elif region in ["timorsea", "timor sea"]:
        latN, latS, lonW, lonE = -10.0, -13.0, 123.0, 129.0
    elif region in ["gulfofalaska", "gulf of alaska"]:
        latN, latS, lonW, lonE = 60.0, 48.0, -145.0, -136.0
    elif region in ["eastchinasea", "east china sea"]:
        latN, latS, lonW, lonE = 35.0, 30.0, 120.0, 128.0
    elif region in ["labradorsea", "labrador sea"]:
        latN, latS, lonW, lonE = 62.0, 50.0, -63.0, -35.0
    elif region in ["seaofokhotsk", "sea of okhotsk"]:
        latN, latS, lonW, lonE = 60.0, 45.0, 142.0, 163.0
    elif region in ["philippinesea", "philippine sea"]:
        latN, latS, lonW, lonE = 25.0, 5.0, 117.0, 135.0
    elif region in ["rosssea", "ross sea"]:
        latN, latS, lonW, lonE = -60.0, -78.0, 160.0, -150.0
    elif region in ["sargassosea", "sargasso sea"]:
        latN, latS, lonW, lonE = 35.0, 20.0, -70.0, -50.0
    elif region in ["andamansea", "andaman sea"]:
        latN, latS, lonW, lonE = 20.0, 6.0, 93.0, 98.0
    elif region in ["weddellsea", "weddell sea"]:
        latN, latS, lonW, lonE = -60.0, -78.0, -45.0, 20.0
    elif region in ["javasea", "java sea"]:
        latN, latS, lonW, lonE = -6.0, -8.0, 105.0, 117.0
    elif region in ["beaufortsea", "beaufort sea"]:
        latN, latS, lonW, lonE = 79.0, 68.0, -140.0, -148.0
    else:
        raise ValueError("Invalid region. Available options: 'Indian Ocean', 'Labrador Sea', 'Global Ocean', 'Atlantic Ocean', 'Pacific Ocean', 'Arctic Ocean', 'Southern Ocean'")
    return latS, latN, lonW, lonE

def convert_longitudes(data):
    """
    Convert longitudes in a given dataset to the range of -180 to 180 degrees.

    Args:
        data (DataArray): Input dataset with longitude coordinates.

    Returns:
        DataArray: Dataset with converted longitudes.

    """
    # Adjust longitudes to the range of -180 to 180 degrees
    data = data.assign_coords(lon=(((data["lon"] + 180) % 360) - 180))

    # Roll the dataset to reposition the prime meridian at the center
    data = data.roll(lon=int(len(data['lon']) / 2), roll_coords=True)
    
    return data



def area_selection(data, region=None, latS: float=None, latN: float=None, lonW: float=None, lonE: float=None):
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

    Raises:
        ValueError: If region is None but the latitude and longitude bounds are not specified.
    """
    if region is None:
        if latN is None or latS is None or lonW is None or lonE is None:
            raise ValueError("When region is None, latN, latS, lonW, lonE values need to be specified.")
        
    else:
        # Obtain latitude and longitude boundaries for the predefined region
        latS, latN, lonW, lonE = predefined_regions(region)
    if lonW < 0 or lonE < 0:
            data = convert_longitudes(data)
    logger.info(f"Selected for this region (latitude {latS} to {latN}, longitude {lonW} to {lonE})")
    # Perform data slicing based on the specified or predefined latitude and longitude boundaries
    data = data.sel(lat=slice(latS, latN), lon=slice(lonW, lonE))
    
    return data

def weighted_zonal_mean(data, region=None, latS: float=None, latN: float=None, lonW: float=None, lonE: float=None):
    """
    Compute the weighted zonal mean of data within the specified latitude and longitude bounds.

    Parameters:
        data (xarray.Dataset): Input data.
        
        region (str, optional): Predefined region name. If provided, latitude and longitude bounds will be fetched from predefined regions.
        
        latS (float, optional): Southern latitude bound. Required if region is not provided or None.
        
        latN (float, optional): Northern latitude bound. Required if region is not provided or None.
        
        lonW (float, optional): Western longitude bound. Required if region is not provided or None.
        
        lonE (float, optional): Eastern longitude bound. Required if region is not provided or None.

    Returns:
        xarray.Dataset: Weighted zonal mean of the input data.
    """
    data = area_selection(data, region, latS =None, latN =None, lonW =None, lonE =None )

    wgted_mean = data.mean(("lon"))
    
    return wgted_mean

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
    data = area_selection(data, region, latS =None, latN =None, lonW =None, lonE =None )
    weighted_data = data.weighted(np.cos(np.deg2rad(data.lat)))
    wgted_mean = weighted_data.mean(("lat", "lon"))
    return wgted_mean

def zonal_mean_trend_plot(data, region=None, latS: float=None, latN: float=None, lonW: float=None,
                            lonE: float=None,  output= True, output_dir = "output"):
    """
    Plots spatial trends at different vertical levels for two variables.

    Args:
    
        data (xarray.Dataset):
            Input dataset containing a single 3D field with trends as a function of depth, latitude, and longitude.
            
        region (str, optional):
            Region name.
            
        latS (float, optional):
            Southern latitude bound for the region.
            
        latN (float, optional):
            Northern latitude bound for the region.
            
        lonW (float, optional):
            Western longitude bound for the region.
            
        lonE (float, optional):
            Eastern longitude bound for the region.
            
        output (bool, optional):
            Flag indicating whether to save the output figure and data. Defaults to True.
            
        output_dir (str, optional):
            Output directory path. Defaults to "output".

    Returns:
        None
    """
    data = TS_3dtrend(data)
    data = weighted_zonal_mean(data, region, latS, latN, lonW, lonE)

    fig, (axs) = plt.subplots(nrows=1, ncols=2, figsize=(14, 5))

    data.ocpt.plot.contourf(levels=20, ax=axs[0])
    axs[0].set_ylim((5500, 0))

    fig.suptitle(f"Zonally-averaged long-term trends in the {region}", fontsize=20)

    plt.subplots_adjust(top=0.85)

    
    axs[0].set_title(f"Temperature", fontsize=14)
    axs[0].set_ylabel("Depth (in m)", fontsize=9)
    axs[0].set_xlabel("Latitude (in deg North)", fontsize=9)
    axs[0].set_facecolor('grey')

    data.so.plot.contourf(levels=20, ax=axs[1])
    axs[1].set_ylim((5500, 0))
    axs[1].set_title(f"Salinity", fontsize=14)
    axs[1].set_ylabel("Depth (in m)", fontsize=12)
    axs[1].set_xlabel("Latitude (in deg North)", fontsize=12)
    axs[1].set_facecolor('grey')

    if output == True:
        output_path, fig_dir, data_dir, filename = dir_creation(data, region, "_", latS, latN, lonE, lonW, output_dir, plot_name= "zonal_mean_trend")

        data.to_netcdf(f'{data_dir}/{filename}.nc')
        plt.savefig(f"{fig_dir}/{filename}.png")
        logger.info(f"Figure and data used for this plot are saved here: {output_path}")
    
    plt.show()

    return

def std_anom_wrt_initial(data, region=None, latS=None, latN=None, lonW=None, lonE=None):
    """
    Compute the standard anomaly with respect to the initial time step of data within the specified latitude and longitude bounds.
    Normalization is done with respect to the standard deviation of the respective vertical level.

    Parameters:
        data (xarray.Dataset): Input data.
        
        region (str, optional): Predefined region name. If provided, latitude and longitude bounds will be fetched from predefined regions.
        
        latS (float, optional): Southern latitude bound. Required if region is not provided or None.
        
        latN (float, optional): Northern latitude bound. Required if region is not provided or None.
        
        lonW (float, optional): Western longitude bound. Required if region is not provided or None.
        
        lonE (float, optional): Eastern longitude bound. Required if region is not provided or None.

    Returns:
        xarray.Dataset: Standardized anomaly with respect to the initial time step of the input data.
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
    data = weighted_area_mean(data, region, latS, latN, lonW, lonE)


    return data


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


def data_process_by_type(data,  type=None):
    """
    Selects the type of timeseries and colormap based on the given parameters.

    Args:
        data (DataArray): Input data containing temperature (ocpt) and salinity (so).
    Returns:
        process_data (Dataset): Processed data based on the selected timeseries type.
        cmap (str): Colormap to be used for the plot.
    """ 
    type = type.lower()
    process_data = xr.Dataset()

    if type in ['anomaly tmean', "anomaly vs tmean","anomaly_tmean", "anomaly_vs_tmean"]:
        cmap = "PuOr"
        for var in list(data.data_vars.keys()):
            process_data[var] = data[var] - data[var].mean(dim='time')
    elif type in ['anomaly t0', "anomaly vs t0", "anomaly_t0", "anomaly_vs_t0"]:
        cmap = "PuOr"
        for var in list(data.data_vars.keys()):
            process_data[var] = data[var] - data[var].isel(time=0)
    elif type in ['stdanomaly_t0',"std_anomaly_vs_t0", "std anomaly t0", "stdanomaly t0"]:
        cmap = "PuOr"
        for var in list(data.data_vars.keys()):
            var_data = data[var] - data[var].isel(time=0)
            var_data.attrs['units'] = 'Stand. Units'
            # Calculate the standard anomaly by dividing the anomaly by its standard deviation along the time dimension
            process_data[var] = var_data / var_data.std(dim="time")
    elif type in ['stdanomaly_tmean',"std_anomaly_vs_tmean", "std anomaly tmean", "stdanomaly tmean"]:
        cmap = "PuOr"
        for var in list(data.data_vars.keys()):
            var_data = data[var] - data[var].mean(dim='time')
            var_data.attrs['units'] = 'Stand. Units'
            # Calculate the standard anomaly by dividing the anomaly by its standard deviation along the time dimension
            process_data[var] = var_data / var_data.std(dim="time")
            
    else:
        cmap='jet'
        process_data = data
    logger.info(f"Data processed for {type}")
    return process_data, cmap

def hovmoller_lev_time_plot(data, region, type= None , latS: float=None, latN: float=None, lonW: float=None,
                            lonE: float=None, output= False, output_dir= "output"):
    """
    Create a Hovmoller plot of temperature and salinity full values.

    Args:
        data (DataArray): Input data containing temperature (ocpt) and salinity (so).
        region (str): Region represented in the plot.
        type (str): Type of timeseries to display, choose from FullValue, Anomaly, StdAnomaly.
        latS (float, optional): Southern latitude boundary of the region. Default is None.
        latN (float, optional): Northern latitude boundary of the region. Default is None.
        lonW (float, optional): Western longitude boundary of the region. Default is None.
        lonE (float, optional): Eastern longitude boundary of the region. Default is None.
        output (bool, optional): Indicates whether to save the plot and data. Default is False.
        output_dir (str, optional): Directory to save the output files. Default is "output".

    Returns:
        None
    """
    data  = weighted_area_mean(data, region, latS, latN, lonW, lonE)
    # Reads the type of timeseries to plot
    data, cmap = data_process_by_type(data, type)
    
    logger.info(f"Hovmoller plotting in process")
    # Create subplots for temperature and salinity plots
    fig, (axs) = plt.subplots(nrows=1, ncols=2, figsize=(14, 5))
    fig.suptitle(f"{type} {region} T,S evolution", fontsize=22)

    if output == True:
        output_path, fig_dir, data_dir, filename = dir_creation(data, region, type, latS, latN, lonE, lonW, output_dir, plot_name= "hovmoller_plot")
    
    import matplotlib.colors as mcolors
    norm = mcolors.TwoSlopeNorm(vcenter=0)

    #plt.pcolor(X, Y, Z, vmin=vmin, vmax=vmax, norm=norm) 

    # To center the colorscale around zero when we plot temperature anomalies
    ocptmin=round(np.min(data.ocpt.values),2)
    ocptmax=round(np.max(data.ocpt.values),2)

    if ocptmin < 0:
        if abs(ocptmin) < ocptmax:
            ocptmin=ocptmax*-1
        else:
            ocptmax=ocptmin*-1
        
        ocptlevs = np.linspace(ocptmin, ocptmax,21)

    else:
        ocptlevs = 20

    # And we do the same for salinity
    somin=round(np.min(data.so.values),3)
    somax=round(np.max(data.so.values),3)

    if somin < 0:
        if abs(somin) < somax:
            somin=somax*-1
        else:
            somax=somin*-1
        
        solevs = np.linspace(somin, somax,21)

    else:
        solevs = 20


    cs1=axs[0].contourf(data.time,data.lev, data.ocpt.transpose(),
                        levels=ocptlevs,cmap= cmap,extend='both')
    cbar_ax = fig.add_axes([0.13, 0.1, 0.35, 0.05])
    cbar = fig.colorbar(cs1, cax=cbar_ax, orientation='horizontal')
    
    
    cs2=axs[1].contourf(data.time,data.lev, data.so.transpose() ,
                        levels=solevs,cmap= cmap,extend='both')
    cbar_ax = fig.add_axes([0.54, 0.1, 0.35, 0.05])
    cbar = fig.colorbar(cs2, cax=cbar_ax, orientation='horizontal')

    
    if output == True:
        data.to_netcdf(f'{data_dir}/{filename}.nc')
        # obs_clim.to_netcdf(f'{data_dir}/{filename}_Rho.nc')
    
    axs[0].invert_yaxis()
    axs[1].invert_yaxis()
  
    axs[0].set_ylim((5500, 0))


    axs[0].set_title("Temperature", fontsize=15)
    axs[0].set_ylabel("Depth (in m)", fontsize=12)
    axs[0].set_xlabel("Time (in years)", fontsize=12)
    
    axs[1].set_title("Salinity", fontsize=15)
    axs[1].set_xlabel("Time (in years)", fontsize=12)
    axs[1].set_yticklabels([])
    
    
    plt.subplots_adjust(bottom=0.3, top=0.85, wspace=0.1)

    if output == True:
        plt.savefig(f"{fig_dir}/{filename}.png")
        logger.info(f"Figure and data used for this plot are saved here: {output_path}")

    return


def time_series_multilevs(data, region=None, type = None, customise_level=False, levels=None, latS: float=None, latN: float=None, lonW: float=None,
                            lonE: float=None,  output= True, output_dir = "output"):
    """
    Create time series plots of global temperature and salinity at selected levels.

    Parameters:
        data (DataArray): Input data containing temperature (ocpt) and salinity (so).
        region (str): Region name.
        type (str): Type of time series, e.g., FullValue, Anomaly, StdAnomaly.
        customise_level (bool): Whether to use custom levels or predefined levels.
        levels (list): List of levels to plot. Ignored if customise_level is False.
        latS (float, optional): Southern latitude bound.
        latN (float, optional): Northern latitude bound.
        lonW (float, optional): Western longitude bound.
        lonE (float, optional): Eastern longitude bound.
        output (bool): Whether to save the plot and data.
        output_dir (str): Directory to save the plot and data.

    Returns:
        None
    """
    data  = weighted_area_mean(data, region, latS, latN, lonW, lonE)
    data, cmap = data_process_by_type(data, type)
    
    logger.info(f"Time series plot is in process")
    
    # Create subplots for temperature and salinity time series plots
    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(16, 5))

    fig.suptitle(f"Spatially Averaged {region} T,S {type}", fontsize=20)

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
        data_level.ocpt.plot.line(ax=axs[0],label=f"{round(int(data_level.lev.data), -2)}")

        # Plot the salinity time series
        data_level.so.plot.line(ax=axs[1],label=f"{round(int(data_level.lev.data), -2)}")
    if output == True:
        output_path, fig_dir, data_dir, filename = dir_creation(data, region, type, latS, latN, lonE, lonW, output_dir, plot_name= "time_series")
        data.to_netcdf(f'{data_dir}/{filename}.nc')
    
    tunits=data_level.ocpt.attrs['units']
    sunits=data_level.so.attrs['units']
    axs[0].set_title("Temperature", fontsize=15)
    axs[0].set_ylabel(f"Potential Temperature (in {tunits})", fontsize=12)
    axs[0].set_xlabel("Time", fontsize=12)
    axs[1].set_title("Salinity", fontsize=15)
    axs[1].set_ylabel(f"Salinity (in {sunits})", fontsize=12)
    axs[1].set_xlabel("Time (in years)", fontsize=12)
    axs[1].legend(loc='right')
    # axs[1].set_yticklabels([])
    plt.subplots_adjust(bottom=0.3, top=0.85, wspace=0.2)

    if output == True:
        plt.savefig(f"{fig_dir}/{filename}.png")
        logger.info(f" Figure and data used in the plot, saved here : {output_path}")
    plt.show()
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
    logger.info("practical salinity converted to absolute salinity")
    # Convert potential temperature to conservative temperature
    ocpt = convert_ocpt(absso, data.ocpt)
    logger.info("potential temperature converted to conservative temperature")
    # Compute potential density in-situ at reference pressure 0 dbar
    rho = compute_rho(absso, ocpt, 0)
    logger.info("Calculated potential density in-situ at reference pressure 0 dbar ")
    # Merge the converted variables into a new dataset
    converted_data = converted_data.merge({"ocpt": ocpt, "so": absso, "rho": rho})

    return converted_data

def linregress_3D(y_array):
    """
    Computes the linear regression against the temporal dimension of a 3D array formatted in time, latitude, and longitude.

    The function is a very efficient way to compute trends in 3D arrays.

    Parameters:
        y_array (np.ndarray): 3D array with time, latitude, and longitude as dimensions.

    Returns:
        n (np.ndarray): Number of non-nan values over each (latitude, longitude) grid box.
        slope (np.ndarray): Slope of the linear regression line over each (latitude, longitude) grid box.
        intercept (np.ndarray): Intercept of the linear regression line over each (latitude, longitude) grid box.
        p_val (np.ndarray): p-value of the linear regression over each (latitude, longitude) grid box.
        r_square (np.ndarray): R-squared value of the linear regression over each (latitude, longitude) grid box.
        rmse (np.ndarray): Root mean squared error (RMSE) of the linear regression over each (latitude, longitude) grid box.
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

def lintrend_3D(y_array):
    """
    Simplified version of linregress_3D that computes the trends in a 4D array formated in time, depth, latitude and longitude coordinates

    It outputs the trends in xarray format

    Parameters
    ----------
    data : y_array.Dataset
    
    Dataset containing a single 4D field with time, depth, latitude and longitude as coordinates
 

    Returns
    -------
    n,slope,intercept,p_val,r_square,rmse

    """
    
    x_array=np.empty(y_array.shape)
    for i in range(y_array.shape[0]): x_array[i,:,:,:]=i+1 # This would be fine if time series is not too long. Or we can use i+yr (e.g. 2019).
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
    trend=xr.DataArray(trend,coords={"lev": y_array.lev,"lat": y_array.lat,"lon": y_array.lon},name=f"{y_array.name} trends",dims=["lev","lat","lon"])
    trend.attrs['units'] = f"{y_array.units}/year"

    #data.ocpt.attrs['units'] = 'Standardised Units'
    return trend

def TS_3dtrend(data):
    """
    Computes the trend values for temperature and salinity variables in a 3D dataset.

    Parameters:
        data (xarray.Dataset): Input dataset containing temperature (ocpt) and salinity (so) variables.

    Returns:
        xarray.Dataset: Dataset with trend values for temperature and salinity variables.
    """
    TS_3dtrend_data = xr.Dataset()

    so = lintrend_3D(data.so)
    ocpt = lintrend_3D(data.ocpt)
    
    TS_3dtrend_data = TS_3dtrend_data.merge({"ocpt": ocpt, "so": so})

    logger.info("Trend value calculated")
    return TS_3dtrend_data


def multilevel_t_s_trend_plot(data, region=None, customise_level=False, levels=None, latS: float=None, latN: float=None, lonW: float=None,
                            lonE: float=None,  output= True, output_dir = "output"):
    """
    Generates a plot showing trends at different depths for temperature and salinity variables.

    Parameters:
        data (xarray.Dataset): Input data containing temperature (ocpt) and salinity (so) variables.
        region (str): Region name.
        customise_level (bool): Whether to use custom levels or predefined levels.
        levels (list): List of levels to plot. Ignored if customise_level is False.
        latS (float): Southern latitude bound.
        latN (float): Northern latitude bound.
        lonW (float): Western longitude bound.
        lonE (float): Eastern longitude bound.
        output (bool): Whether to save the plot and data.
        output_dir (str): Output directory to save the plot and data.

    Returns:
        None
    """  
    data = area_selection(data, region, latS, latN, lonE, lonW)
    data = TS_3dtrend(data)

    # Define the levels for plotting
    if customise_level:
        if levels is None:
            raise ValueError("Custom levels are selected, but levels are not provided.")
    else:
        levels = [10, 100, 500, 1000, 3000, 5000]

    # To fix the dimensions so that all subpanels are well visible
    dim1=16
    dim2=5*len(levels)

    
    fig, axs = plt.subplots(nrows=len(levels), ncols=2, figsize=(dim1, dim2))

    fig.subplots_adjust(hspace=0.18,wspace=0.15,top=0.95)
    for levs in range(len(levels)):
        
        
        data["ocpt"].interp(lev=levels[levs]).plot.contourf(ax=axs[levs,0],levels=18)
        data["so"].interp(lev=levels[levs]).plot.contourf(ax=axs[levs,1], levels=18)
        
        
        axs[levs,0].set_ylabel("Latitude (in deg North)", fontsize=9)
        axs[levs,0].set_facecolor('grey')
        # axs[levs, 0].set_aspect('equal', adjustable='box')
        
        axs[levs, 1].set_yticklabels([])
        
        if levs == (len(levels)-1):
            axs[levs,0].set_xlabel("Longitude (in de East)", fontsize=12)
            axs[levs,0].set_ylabel("Latitude (in deg North)", fontsize=12)
            
        if levs != (len(levels)-1):
            axs[levs, 0].set_xticklabels([])
            axs[levs, 1].set_xticklabels([])
        axs[levs,1].set_facecolor('grey')
        # axs[levs, 1].set_aspect('equal', adjustable='box')
 
    
    plt.suptitle(f'Linear Trends of T,S at different depths in the {region.replace("_"," ").capitalize()}', fontsize=24)
    axs[0,0].set_title("Temperature", fontsize=18)
    axs[0,1].set_title("Salinity", fontsize=18)
    if output == True:
        output_path, fig_dir, data_dir, filename = dir_creation(data, region, "_", latS, latN, lonE, lonW, output_dir, plot_name= "multilevel_t_s_trend")

        data.interp(lev=levels[levs]).to_netcdf(f'{data_dir}/{filename}.nc')
        plt.savefig(f"{fig_dir}/{filename}.png")
        logger.info(f"Figure and data used for this plot are saved here: {output_path}")
    
    plt.show()

    return



   
def split_time_equally(data):
    """
    Splits the input data into two halves based on time dimension, or returns the original data if it has only one time step.

    Parameters:
        data (xarray.Dataset): Input data.

    Returns:
        list: A list containing the original data and the two halves of the data.
    """
    date_len = len(data.time)
    data_1 = None
    data_2 = None
    if date_len == 0:
        raise("Time lenth is 0 in the data")
    elif date_len == 1:
        data = data
    else :
        data = None
        if date_len % 2 == 0:
            data_1 = data.isel(time=slice(0, int(date_len/2)))
            data_2 = data.isel(time=slice(int(date_len/2), date_len))
        else:
            data_1 = data.isel(time=slice(0, int((date_len-1)/2)))
            data_2 = data.isel(time=slice(int((date_len-1)/2), date_len))
    return [data, data_1, data_2]


def load_obs_data(model='EN4',exp='en4',source='monthly'):
    """
    Load observational data for ocean temperature and salinity.

    Parameters:
        model (str): Model name.
        exp (str): Experiment name.
        source (str): Data source.

    Returns:
        xarray.Dataset: Observational data containing ocean temperature and salinity.
    """
    reader = Reader(model,exp,source)
    den4=reader.retrieve()
    den4=den4.rename({"depth":"lev"}) # We standardise the name for the vertical dimension
    den4=den4[["ocpt","so"]].resample(time="M").mean()
    logger.info(f"loaded {model} data")
    return den4
    
def crop_obs_overlap_time(mod_data, obs_data):
    """
    Crop the observational data to the overlapping time period with the model data.

    Parameters:
        mod_data (xarray.Dataset): Model data.
        obs_data (xarray.Dataset): Observational data.

    Returns:
        xarray.Dataset: Observational data cropped to the overlapping time period with the model data.
    """
    mod_data_time= mod_data.time  
    obs_data_time=obs_data.time
    common_time = xr.DataArray(np.intersect1d(mod_data_time, obs_data_time), dims='time')
    if len(common_time) > 0:
        obs_data = obs_data.sel(time=common_time)
        logger.info("selected the overlaped time of the obs data compare to the model")
    return obs_data

def prepare_data_for_stratification_plot(data, region=None, time = None, latS: float=None, latN: float=None, lonW: float=None,
                            lonE: float=None):
    """
    Prepare data for plotting stratification profiles.

    Parameters:
        data (xarray.Dataset): Input data containing temperature (ocpt) and salinity (so).
        region (str, optional): Region name.
        time (str or list, optional): Time period to select. Can be a single date or a list of start and end dates.
        latS (float, optional): Southern latitude bound. Required if region is not provided or None.
        latN (float, optional): Northern latitude bound. Required if region is not provided or None.
        lonW (float, optional): Western longitude bound. Required if region is not provided or None.
        lonE (float, optional): Eastern longitude bound. Required if region is not provided or None.

    Returns:
        xarray.Dataset: Prepared data for plotting stratification profiles.
    """
    data = weighted_area_mean(data, region, latS, latN, lonE, lonW)
    data = convert_variables(data)
    data_rho = data["rho"] -1000
    data["rho"] = data_rho
    data = data_time_selection(data, time)
    return data

def data_time_selection(data, time):
    """
    Selects the data based on the specified time period.

    Parameters:
        data (xarray.Dataset): Input data.
        time (str): Time period selection.

    Returns:
        xarray.Dataset: Data for the selected time period.
    """    
    time = time.lower()
    if time in ["jan", "january", "1", 1]:
        data = data.where(data.time.dt.month == 1, drop=True)
    elif time in ["feb", "february", "2", 2]:
        data = data.where(data.time.dt.month == 2, drop=True)
    elif time in ["mar", "march", "3", 3]:
        data = data.where(data.time.dt.month == 3, drop=True)
    elif time in ["apr", "april", "4",4]:
        data = data.where(data.time.dt.month == 4, drop=True)
    elif time in ["may", "5", 5]:
        data = data.where(data.time.dt.month == 5, drop=True)
    elif time in ["jun", "june", "6", 6]:
        data = data.where(data.time.dt.month == 6, drop=True)
    elif time in ["jul", "july", "7", 7]:
        data = data.where(data.time.dt.month == 7, drop=True)
    elif time in ["aug", "august", "8", 8]:
        data = data.where(data.time.dt.month == 8, drop=True)
    elif time in ["sep", "sept", "september", "9", 9]:
        data = data.where(data.time.dt.month == 9, drop=True)
    elif time in ["oct", "october", "10", 10]:
        data = data.where(data.time.dt.month == 10, drop=True)
    elif time in ["nov", "november", "11", 11]:
        data = data.where(data.time.dt.month == 11, drop=True)
    elif time in ["dec", "december", "12", 12]:
        data = data.where(data.time.dt.month == 12, drop=True)
    elif time in ["yearly", "year", "y"]:
        data = data.groupby('time.year').mean(dim='time')
    if time in ["jja", "jun_jul_aug", "jun-jul-aug", "june-july-august", "june_july_august"]:
        data = data.where((data['time.month'] >= 6) & (data['time.month'] <= 8), drop=True)
    elif time in ["fma", "feb_mar_apr", "feb-mar-apr", "february-march-april", "february_march_april"]:
        data = data.where((data['time.month'] >= 2) & (data['time.month'] <= 4), drop=True)
    elif time in ["djf", "dec_jan_feb", "dec-jan-feb", "december-january-february", "december_january_february"]:
        data = data.where((data['time.month'] == 12) | (data['time.month'] <= 2), drop=True)
    elif time in ["son", "sep_oct_nov", "sep-oct-nov", "september-october-november", "september_october_november"]:
        data = data.where((data['time.month'] >= 9) & (data['time.month'] <= 11), drop=True)
    else:
        raise ValueError("""Invalid month input. Please provide a valid name. Among this:
                         Yearly, 3M, Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec """)
    logger.info(f"data selected for {time} climatology")
    return data


def compare_arrays(mod_data, obs_data):
    """
    Compares the time scale of model data and observed data and selects the overlapping time periods.

    Parameters:
        mod_data (xarray.Dataset): Model data.
        obs_data (xarray.Dataset): Observed data.

    Returns:
        list: List of model data arrays with overlapping time periods.
        obs_data_selected (xarray.Dataset): Observed data for the overlapping time periods.
    """
    if (obs_data.time == mod_data.time).all() and (len(mod_data.time) == len(obs_data.time)):
        mod_data_list = [mod_data]
        obs_data_selected = obs_data
        logger.info("obs data and model data time scale fully matched")
    elif (obs_data.time == mod_data.time).any():
        mod_data_ov = mod_data.sel(time=obs_data.time)
        mod_data_list= [mod_data_ov, mod_data]
        obs_data_selected = obs_data
        logger.info("Model and Obs data time partly matched")
    else:
        mod_data_list = split_time_equally(mod_data)
        obs_data_selected = None
        logger.info("Model data time is not avaiable for the obs data")
    
    return mod_data_list, obs_data_selected

def dir_creation(data, region=None, sp_value = None, latS: float=None, latN: float=None, lonW: float=None,
                            lonE: float=None, output_dir= None , plot_name = None):
    """
    Creates the directory structure for saving the output data and figures.

    Parameters:
        data (xarray.Dataset): Data used for the plot.
        region (str): Region name.
        sp_value (str): Value specific to the plot.
        latS (float): Southern latitude bound.
        latN (float): Northern latitude bound.
        lonW (float): Western longitude bound.
        lonE (float): Eastern longitude bound.
        output_dir (str): Directory path for saving the output.
        plot_name (str): Name of the plot.

    Returns:
        tuple: Output path, figure directory path, data directory path, and filename.
    """
    if output_dir == None:
        raise("Please provide the outut_dir when output = True")
    if region in [None, "custom", "Custom"]:
        region = "custom"
        filename = f"{plot_name}_{sp_value}_{region.replace(' ', '_').lower()}_lat_{latS}_{latN}_lon_{lonW}_{lonE}_mean"
    else: 
        filename = f"{plot_name}_{sp_value}_{region.replace(' ', '_').lower()}_mean"
    
    current_time = f'{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}'
    output_path = f"{output_dir}/{filename}_{current_time}"
    fig_dir = f"{output_path}/figs"
    data_dir = f"{output_path}/data"
    os.makedirs(fig_dir)
    os.makedirs(data_dir)
    return output_path, fig_dir, data_dir, filename


def plot_stratification(mod_data, region=None, time = None, latS: float=None, latN: float=None, lonW: float=None,
                            lonE: float=None,  output= True, output_dir = "output"):
    """
    Create a stratification plot showing the mean state temperature, salinity, and density profiles.

    Parameters:
        mod_data (xarray.Dataset): Model data.
        region (str): Region name.
        time (str): Time selection for data (e.g., 'yearly', '3M', 'Jan', 'Feb', etc.).
        latS (float): Southern latitude bound.
        latN (float): Northern latitude bound.
        lonW (float): Western longitude bound.
        lonE (float): Eastern longitude bound.
        output (bool): Flag indicating whether to save the output.
        output_dir (str): Directory path for saving the output.

    Returns:
        None
    """
    obs_data= load_obs_data().interp(lev=mod_data.lev)
    obs_data= crop_obs_overlap_time(mod_data, obs_data)
    
    obs_data = prepare_data_for_stratification_plot(obs_data, region, time, latS, latN, lonE, lonW)
    mod_data = prepare_data_for_stratification_plot(mod_data, region, time, latS, latN, lonE, lonW)
    mod_data_list, obs_data=  compare_arrays(mod_data, obs_data)
    
    mod_data_list = list(filter(lambda value: value is not None, mod_data_list))

    fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(14, 8))
    logger.info("Stratification plot is in process")
    
    
    if output == True:
        output_path, fig_dir, data_dir, filename = dir_creation(mod_data, region, time, latS, latN, lonE, lonW, output_dir, plot_name= "stratification")
    
    
    legend_list = []
    for i, var in zip(range(len(axs)), ["ocpt", "so", "rho"]):
        axs[i].set_ylim((4500, 0))
        data_1 = mod_data_list[0][var].mean("time")
        
        axs[i].plot(data_1, data_1.lev, 'g-', linewidth=2.0)
        legend_info = f"Model {mod_data_list[0].time[0].dt.year.data}-{mod_data_list[0].time[-1].dt.year.data}"
        legend_list.append(legend_info)
        if output == True: data_1.to_netcdf(f'{data_dir}/{filename}_{legend_info.replace(" ","_")}.nc')
        
        
        if len(mod_data_list) > 1:
            data_2 = mod_data_list[1][var].mean("time")
            axs[i].plot(data_2, data_2.lev, 'b-', linewidth=2.0)
            legend_info = f"Model {mod_data_list[1].time[0].dt.year.data}-{mod_data_list[1].time[-1].dt.year.data}"
            legend_list.append(legend_info)
            if output == True: data_2.to_netcdf(f'{data_dir}/{filename}_{legend_info.replace(" ","_")}.nc')
        if obs_data != None:
            data_3 = obs_data[var].mean("time")
            axs[i].plot(data_3, data_3.lev, 'r-', linewidth=2.0)
            legend_info = f"Obs {obs_data.time[0].dt.year.data}-{obs_data.time[-1].dt.year.data}"
            legend_list.append(legend_info)
            if output == True: data_3.to_netcdf(f'{data_dir}/{filename}_{legend_info.replace(" ","_")}.nc')
        
    fig.suptitle(f"Mean state {time.upper()} T, S, rho0 stratification in {region}", fontsize=20)
    axs[0].set_title("Temperature Profile", fontsize=14)
    axs[0].set_ylabel("Depth (m)", fontsize=15)
    axs[0].set_xlabel("Temperature (°C)", fontsize=12)

    axs[1].set_title("Salinity Profile", fontsize=14)
    axs[1].set_xlabel("Salinity (psu)", fontsize=12)
    # axs[1].set_ylabel("", fontsize=0)
    axs[1].set_yticklabels([]) 

    axs[2].set_title("Rho (ref 0) Profile", fontsize=14)
    axs[2].set_xlabel("Density Anomaly (kg/m³)", fontsize=12)
    # axs[2].set_ylabel("", fontsize=0)
    axs[2].set_yticklabels([]) 

    axs[0].legend(legend_list, loc='best')

    if output == True:
        plt.savefig(f"{fig_dir}/{filename}.png")
        logger.info(f" Figure and data used in the plot, saved here : {output_path}")
    plt.show()
    return 
    



def compute_mld_cont(rho):
    """To compute the mixed layer depth from density fields in continous levels
    using the same criteria as in de Boyer and Montegut (2004). The continuous distribution of MLD
    values is achieved by performing an interpolation between the first level that exceeds the
    threshold and the one immediately after to linearly estimate where the 0.03 value would be reached

    Warning!!: It does not provide reasonable estimates in some instances in which the upper level 
    has higher densities than the lower one. This function is therefore not recommended until this
    issue is addressed and corrected

    Parameters
    ----------
    rho : xarray.DataArray for sigma0, dims must be time, space, depth (must be in metres)
    Returns
    -------
    mld: xarray.DataArray, dims of time, space
    
      
    """
    # Here we identify the first level to represent the surfac
    surf_dens= rho.isel(lev=slice(0,1)).mean("lev") 

    # We compute the density anomaly between surface and whole field
    dens_ano = rho-surf_dens
    
    # We define now a sigma difference wrt to the threshold of 0.03 kg/m3 in de Boyer Montegut (2004)
    dens_diff=dens_ano-0.03

    # Now we only keep the levels for which the threshold has not been surpassed
    dens_diff2 = dens_diff.where(dens_diff < 0)   ### The threshold in de Boyer Montegut (2004)

    # And keep the deepest one
    cutoff_lev1=dens_diff2.lev.where(dens_diff2>-9999).max(["lev"]) 
    # And the following one (for which the threshold will have been overcome)
    cutoff_lev2=dens_diff2.lev.where(dens_diff2.lev > cutoff_lev1).min(["lev"])
    
    depth=rho.lev.where(rho > -9999).max(["lev"]) # Here we identify the last level of the ocean
   
    ddif=cutoff_lev2-cutoff_lev1
    # The MLD is established by linearly interpolating to the level on which the difference wrt to the reference is zero
    rdif1=dens_diff.where(dens_diff.lev==cutoff_lev1).max(["lev"])  #rho diff in first lev
    
    rdif2=dens_diff.where(dens_diff.lev==cutoff_lev2).max(["lev"]) # rho diff in second lev
    mld=cutoff_lev1+((ddif)*(rdif1))/(rdif1-rdif2)
    mld=np.fmin(mld,depth) # The MLD is set as the maximum depth if the threshold is not exceeded before
    # mld=mld.rename("mld")
    
    return mld    

def data_for_plot_spatial_mld(data, region=None, time = None, latS: float=None, latN: float=None, lonW: float=None,
                            lonE: float=None):
    data = area_selection(data, region, latS, latN, lonE, lonW)
    data = convert_variables(data)
    data = compute_mld_cont(data)
    data = data_time_selection(data, time)
    
    return data

        

def plot_spatial_mld(mod_data, region=None, time = None, latS: float=None, latN: float=None, lonW: float=None,
                            lonE: float=None, output= False, output_dir= "output"):
    """
    Plots the climatology of mixed layer depth in the NH as computed with de Boyer Montegut (2004)'s criteria in 
    an observational dataset and a model dataset, allowing the user to select the month the climatology is computed
    (the recommended one is march (month=3) that is when the NH MLD peaks)

    Parameters
    ----------
    datamod : xarray.Dataset
        Model Dataset containing 2D fields of density (rho).
    dataobs : xarray.Dataset
        Observational dataset containing 2D fields of density (rho)
    month : integer
        Number of the month on which to compute the climatologies

    Returns
    -------
    None

    """
    
    mod_clim=data_for_plot_spatial_mld(mod_data, region, time, latS, latN, lonE, lonW).mean("time") # To select the month and compute its climatology
    obs_data = load_obs_data(model='EN4',exp='en4',source='monthly')
    obs_clim=data_for_plot_spatial_mld(obs_data, region, time, latS, latN, lonE, lonW).mean("time") # To select the month and compute its climatology
    obs_data= crop_obs_overlap_time(mod_data, obs_data)

    mod_clim = mod_clim["rho"]
    obs_clim = obs_clim["rho"]
    
    if output == True:
        output_path, fig_dir, data_dir, filename = dir_creation(mod_data, region, time, latS, latN, lonE, lonW, output_dir, plot_name= "spatial_MLD")
    
    logger.info("Spatial MLD plot is in process")
    fig, axs = plt.subplots(nrows=1, ncols=2, subplot_kw={'projection': ccrs.PlateCarree()}, figsize=(22, 8),)

    
    fig.suptitle(f'Mean state of {time.upper()} mixed layer depth in {region.replace("_"," ").upper()}', fontsize=27)
    
    cs1=axs[0].contourf(mod_clim.lon,mod_clim.lat,mod_clim, projection=ccrs.PlateCarree(),
                        levels=np.linspace(np.min(mod_clim),np.max(mod_clim),27),cmap='seismic',extend='both')
    
    cs1=axs[1].contourf(obs_clim.lon,obs_clim.lat,obs_clim, projection=ccrs.PlateCarree(),
                        levels=np.linspace(np.min(mod_clim),np.max(mod_clim),27),cmap='seismic',extend='both')
    
    if output == True:
        mod_clim.to_netcdf(f'{data_dir}/{filename}_Rho.nc')
        obs_clim.to_netcdf(f'{data_dir}/{filename}_Rho.nc')
    
    axs[0].set_title("Model climatology", fontsize=18)
    axs[0].set_ylabel("Latitude", fontsize=14)
    axs[0].set_xlabel("Longitude", fontsize=14)

    axs[1].set_title("OBS climatology", fontsize=18)
    # axs[1].set_ylabel("Latitude", fontsize=12)
    axs[1].set_xlabel("Longitude", fontsize=14)
    axs[1].set_yticklabels([]) 

    
    cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])  # Adjust the position and size as needed
    fig.colorbar(cs1, cax=cbar_ax)
    
    gl = axs[0].gridlines(crs=ccrs.PlateCarree(), draw_labels=True,linewidth=0,)
    gl.top_labels = False
    gl.bottom_labels = True
    gl.right_labels = False
    
    gl = axs[1].gridlines(crs=ccrs.PlateCarree(), draw_labels=True,linewidth=0,)
    gl.top_labels = False
    gl.bottom_labels = True
    gl.right_labels = False
    gl.left_labels = False

    plt.subplots_adjust(top=0.85, wspace=0.1)
    axs[0].coastlines()
    axs[1].coastlines()
    
    if output == True:
        plt.savefig(f"{fig_dir}/{filename}.png")
        logger.info(f"Figure and data used for this plot are saved here: {output_path}")
    
    plt.show()
    return
