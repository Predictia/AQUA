
from .tools import *

def data_process_by_type(data, anomaly: bool = False,
                         standardise: bool = False, anomaly_ref: str = None):
    """
    Selects the type of timeseries and colormap based on the given parameters.

    Args:
        data (DataArray): Input data containing temperature (ocpt) and salinity (so).
        anomaly (bool, optional): Specifies whether to compute anomalies. Defaults to False.
        standardise (bool, optional): Specifies whether to standardize the data. Defaults to False.
        anomaly_ref (str, optional): Reference for the anomaly computation. Valid options: "t0", "tmean". Defaults to None.

    Returns:
        process_data (Dataset): Processed data based on the selected preprocessing approach.
        type (str): Type of preprocessing approach applied
        cmap (str): Colormap to be used for the plot.
    """

    process_data = xr.Dataset()

    if anomaly:
        anomaly_ref = anomaly_ref.lower().replace(" ", "").replace("_", "")
        if not standardise:
            if anomaly_ref in ['tmean', "meantime", "timemean"]:
                cmap = "PuOr"
                for var in list(data.data_vars.keys()):
                    process_data[var] = data[var] - data[var].mean(dim='time')
                type = "anomaly wrt temporal mean"
            elif anomaly_ref in ['t0', "intialtime", "firsttime"]:
                cmap = "PuOr"
                for var in list(data.data_vars.keys()):
                    process_data[var] = data[var] - data[var].isel(time=0)
                type = "anomaly wrt initial time"
            else:
                raise ValueError(
                    "Select proper value of anomaly_ref: t0 or tmean, when anomaly = True ")
            logger.info(f"Data processed for {type}")
        if standardise:
            if anomaly_ref in ['t0', "intialtime", "firsttime"]:
                cmap = "PuOr"
                for var in list(data.data_vars.keys()):
                    var_data = data[var] - data[var].isel(time=0)
                    var_data.attrs['units'] = 'Stand. Units'
                    # Calculate the standard anomaly by dividing the anomaly by its standard deviation along the time dimension
                    process_data[var] = var_data / var_data.std(dim="time")
                type = "Std. anomaly wrt initial time"
            elif anomaly_ref in ['tmean', "meantime", "timemean"]:
                cmap = "PuOr"
                for var in list(data.data_vars.keys()):
                    var_data = data[var] - data[var].mean(dim='time')
                    var_data.attrs['units'] = 'Stand. Units'
                    # Calculate the standard anomaly by dividing the anomaly by its standard deviation along the time dimension
                    process_data[var] = var_data / var_data.std(dim="time")
                type = "Std. anomaly wrt temporal mean"
            else:
                raise ValueError(
                    "Select proper value of type: t0 or tmean, when anomaly = True ")
            logger.info(
                f"Data processed for {type}")

    else:
        cmap = 'jet'
        logger.info("Data processed for Full values as anomaly = False")
        type = "Full values"

        process_data = data
    # logger.info(f"Data processed for {type}")
    return process_data, type, cmap

def data_for_hovmoller_lev_time_plot(data):
    data_info = {}
    for anomaly in [False,True]:
        for standardise in [False,True]:
            for anomaly_ref in ["t0","tmean"]:
                data, type, cmap = data_process_by_type(
                    data, anomaly, standardise, anomaly_ref)
                key = (anomaly, standardise, anomaly_ref)
                data_info[key] = {"data": data, "type": type, "cmap": cmap}
                
    return data_info
 
 
def hovmoller_lev_time_plot(o3d_request, anomaly: bool = False,
                            standardise: bool = False, anomaly_ref=None
                            ):
    """
    Create a Hovmoller plot of temperature and salinity full values.

    Parameters:
        data (DataArray): Input data containing temperature (ocpt) and salinity (so).
        region (str): Region represented in the plot.
        anomaly (bool): To decide whether to compute anomalies. Default is False.
        standardise (bool): To decide whether to standardise the anomalies. Default is False.
        anomaly_ref (str): Reference for computing the anomaly (t0=first time step, tmean=whole temporal period; only valid if anomaly is True)
        latS (float): Southern latitude boundary of the region. Default is None. (Optional)
        latN (float): Northern latitude boundary of the region. Default is None. (Optional)
        lonW (float): Western longitude boundary of the region. Default is None. (Optional)
        lonE (float): Eastern longitude boundary of the region. Default is None. (Optional)
        output (bool): Indicates whether to save the plot and data. Default is False. (Optional)
        output_dir (str): Directory to save the output files. Default is None. (Optional)

    Returns:
        None
    """
    data = o3d_request.get('data')
    model = o3d_request.get('model')
    exp = o3d_request.get('exp')
    source = o3d_request.get('source')
    region = o3d_request.get('region', None)
    latS = o3d_request.get('latS', None)
    latN = o3d_request.get('latN', None)
    lonW = o3d_request.get('lonW', None)
    lonE = o3d_request.get('lonE', None)
    output = o3d_request.get('output')
    output_dir = o3d_request.get('output_dir')
    
    
    data = weighted_area_mean(data, region, latS, latN, lonW, lonE)
    # Reads the type of timeseries to plot
    data_info = data_for_hovmoller_lev_time_plot(data)

    logger.info("Hovmoller plotting in process")
    # Create subplots for temperature and salinity plots
    fig, (axs) = plt.subplots(nrows=1, ncols=2, figsize=(14, 5))
    region_title = custom_region(region=region, latS=latS, latN=latN, lonW=lonW, lonE=lonE)
    fig.suptitle(f"Spatially averaged {region_title} T,S {type}", fontsize=22)

    if output:
        output_path, fig_dir, data_dir, filename = dir_creation(data,
            region, latS, latN, lonW, lonE, output_dir, plot_name=f'hovmoller_plot_{type.replace(" ","_")}')


    # plt.pcolor(X, Y, Z, vmin=vmin, vmax=vmax, norm=norm)

    # To center the colorscale around zero when we plot temperature anomalies
    ocptmin = round(np.nanmin(data.ocpt.values), 2)
    ocptmax = round(np.nanmax(data.ocpt.values), 2)

    if ocptmin < 0:
        if abs(ocptmin) < ocptmax:
            ocptmin = ocptmax*-1
        else:
            ocptmax = ocptmin*-1

        ocptlevs = np.linspace(ocptmin, ocptmax, 21)

    else:
        ocptlevs = 20

    # And we do the same for salinity
    somin = round(np.nanmin(data.so.values), 3)
    somax = round(np.nanmax(data.so.values), 3)

    if somin < 0:
        if abs(somin) < somax:
            somin = somax*-1
        else:
            somax = somin*-1

        solevs = np.linspace(somin, somax, 21)

    else:
        solevs = 20

    cs1 = axs[0].contourf(data.time, data.lev, data.ocpt.transpose(),
                          levels=ocptlevs, cmap=cmap, extend='both')
    cbar_ax = fig.add_axes([0.13, 0.1, 0.35, 0.05])
    fig.colorbar(cs1, cax=cbar_ax, orientation='horizontal', label=f'Potential temperature in {data.ocpt.attrs["units"]}')

    cs2 = axs[1].contourf(data.time, data.lev, data.so.transpose(),
                          levels=solevs, cmap=cmap, extend='both')
    cbar_ax = fig.add_axes([0.54, 0.1, 0.35, 0.05])
    fig.colorbar(cs2, cax=cbar_ax, orientation='horizontal', label=f'Salinity in {data.so.attrs["units"]}')

    if output:
        data.to_netcdf(f'{data_dir}/{filename}.nc')
        # obs_clim.to_netcdf(f'{data_dir}/{filename}_Rho.nc')

    axs[0].invert_yaxis()
    axs[1].invert_yaxis()

    axs[0].set_ylim((max(data.lev).data, 0))
    axs[1].set_ylim((max(data.lev).data, 0))

    axs[0].set_title("Temperature", fontsize=15)
    axs[0].set_ylabel("Depth (in m)", fontsize=12)
    axs[0].set_xlabel("Time (in years)", fontsize=12)
    axs[0].set_xticklabels(axs[0].get_xticklabels(), rotation=30)
    axs[1].set_xticklabels(axs[0].get_xticklabels(), rotation=30)
    max_num_ticks = 5  # Adjust this value to control the number of ticks
    from matplotlib.ticker import MaxNLocator
    locator = MaxNLocator(integer=True, prune='both', nbins=max_num_ticks)
    axs[0].xaxis.set_major_locator(locator)
    axs[1].xaxis.set_major_locator(locator)

    axs[1].set_title("Salinity", fontsize=15)
    axs[1].set_xlabel("Time (in years)", fontsize=12)
    axs[1].set_yticklabels([])

    plt.subplots_adjust(bottom=0.3, top=0.85, wspace=0.1)

    if output:
        plt.savefig(f"{fig_dir}/{filename}.pdf")
        logger.info(
            "Figure and data used for this plot are saved here: %s", output_path)

    return
