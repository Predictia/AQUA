"""A module for atmospheric global biases analysis and visualization."""

import os
import xarray as xr
import numpy as np
import matplotlib.pylab as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.gridspec as gridspec
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from aqua import Reader

outputfig = "./output/figs"
if not os.path.exists(outputfig):
    os.makedirs(outputfig)
outputdir = "./output/data"    
if not os.path.exists(outputdir):
    os.makedirs(outputdir)
    

def seasonal_bias(dataset1, dataset2, var_name, year, plev, statistic, model_label1, model_label2):
    '''
    Plot the seasonal bias maps between two datasets for a specific variable and year.

    Args:

        dataset1 (xarray.Dataset): The first dataset
        dataset2 (xarray.Dataset): The second dataset. Note: If this dataset is data_era5 (ERA5 data) it provides a bias calculation with
                                    respect to the ERA5 climatology from 2000 to 2020. You can choose like for dataset1 OR data_era5
        var_name (str): The name of the variable to compare (Examples: 2t, tprate, mtntrf, mtnsrf,...)
        year (int): The year for which to calculate the bias.
        plev (float or None): The desired pressure level in Pa. If None, the variable is assumed to be at surface level.
        statistic (str): The desired statistic to calculate for each season. Valid options are: 'mean', 'max', 'min', 'diff', and 'std'.
        model_label1 and model_label2 (str): The desired labeling for the plot title and the filename for the respective datasets.

    Raises:
        ValueError: If an invalid statistic is provided.

    Returns:
        A seasonal bias plot.
    '''
    
    var1 = dataset1[var_name]
    var2 = dataset2[var_name]
    
    reader_era5 = Reader(model="ERA5", exp="era5", source="monthly")
    data_era5 = reader_era5.retrieve(fix=True)
    data_era5 = data_era5.sel(time=slice('2000-01-01', '2020-12-31'))
    

#     reader_tco2559 = Reader(model = 'IFS', exp = 'tco2559-ng5-cycle3', source = 'lra-r100-monthly')
#     data_tco2559 = reader_tco2559.retrieve(fix = False)

#     reader_tco1279 = Reader(model="IFS", exp="tco1279-orca025-cycle3",source =  'lra-r100-monthly')
#     data_tco1279 = reader_tco1279.retrieve(fix = False)

#     reader_icon = Reader(model = "ICON", exp = "ngc3028", source = 'lra-r100-monthly')
#     data_icon = reader_icon.retrieve(fix = False)

    
    var1_year = var1.sel(time=var1.time.dt.year == year)
    var2_year = var2.sel(time=var2.time.dt.year == year)

    # Select the desired pressure level if provided
    if plev is not None:
        var1_year = var1_year.sel(plev=plev)
        var2_year = var2_year.sel(plev=plev)

    # Calculate the desired statistic for each season
    season_ranges = {'DJF': [12, 1, 2], 'MAM': [3, 4, 5], 'JJA': [6, 7, 8], 'SON': [9, 10, 11]}
    results = []
    for season, months in season_ranges.items():
        if dataset1 == data_era5:
            var1_season = var1.sel(time=var1.time.dt.month.isin(months))
        else:
            var1_season = var1.sel(time=(var1.time.dt.year == year) & (var1.time.dt.month.isin(months)))
        var2_season = var2.sel(time=var2.time.dt.month.isin(months))

        if statistic == 'mean':
            result_season = var2_season.mean(dim='time') - var1_season.mean(dim='time')
        elif statistic == 'max':
            result_season = var2_season.max(dim='time') - var1_season.max(dim='time')
        elif statistic == 'min':
            result_season = var1_season.min(dim='time') - var2_season.min(dim='time')
        elif statistic == 'diff':
            result_season = var1_season - var2_season
        elif statistic == 'std':
            result_season = var1_season.std(dim='time') - var2_season.std(dim='time')
        else:
            raise ValueError("Invalid statistic. Please choose one of 'mean', 'std', 'max', 'min', or 'diff'.")

        results.append(result_season)
    # Create a cartopy projection
    projection = ccrs.PlateCarree()

    # Calculate the number of rows and columns for the subplot grid
    num_rows = 2
    num_cols = 2

    
    # Plot the bias maps for each season
    fig = plt.figure(figsize=(15, 10))
    gs = gridspec.GridSpec(num_rows, num_cols, figure=fig)

    # Create a list to store the plotted objects
    cnplots = []

    for i, (result, season) in enumerate(zip(results, season_ranges.keys())):
        ax = fig.add_subplot(gs[i], projection=projection)

        # Add coastlines to the plot
        ax.add_feature(cfeature.COASTLINE)

        # Add other cartographic features (optional)
        ax.add_feature(cfeature.LAND, facecolor='lightgray')
        ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
        # Set latitude and longitude tick labels
        ax.set_xticks(np.arange(-180, 181, 60), crs=projection)
        ax.set_yticks(np.arange(-90, 91, 30), crs=projection)
        ax.xaxis.set_major_formatter(LongitudeFormatter())
        ax.yaxis.set_major_formatter(LatitudeFormatter())


        # Plot the bias data using the corresponding cnplot object
        cnplot = result.plot(ax=ax, cmap='RdBu_r', add_colorbar = False)
        cnplots.append(cnplot)

        # ax.add_feature(cfeature.OCEAN)
        ax.set_title(f'{season}')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')

    # Remove any empty subplots if the number of results is less than the number of subplots
    if len(results) < num_rows * num_cols:
        for i in range(len(results), num_rows * num_cols):
            fig.delaxes(fig.axes[i])

    # Add a colorbar
    cbar_ax = fig.add_axes([0.25, 0.05, 0.5, 0.02])  # Adjust the position and size of the colorbar
    cbar = fig.colorbar(cnplots[0], cax=cbar_ax, orientation='horizontal')
    cbar.set_label(f'Bias [{var2.units}]')

    # Set the overall figure title
    # Set the overall title        

    if dataset2 == data_era5:

        if plev is not None:
            overall_title = f'Bias of {var_name} ({dataset2[var_name].long_name}) [{var2.units}] ({statistic}) at {plev} Pa\n Experiment {model_label1} {year} with respect to ERA5 climatology (2000-2020)'
        else:
            overall_title = f'Bias of {var_name} ({dataset2[var_name].long_name}) [{var2.units}] ({statistic})\n Experiment {model_label1}  {year} with respect to ERA5 climatology (2000-2020)'
                
    else:
        if plev is not None:
            overall_title = f'Bias of {var_name} ({dataset2[var_name]}) [{var2.units}] ({statistic})\n Experiment {model_label1}  {year} with respect to {model_label2}'
        else:
            overall_title = f'Bias of {var_name} ({dataset2[var_name]}) [{var2.units}] ({statistic}) at {plev} Pa\n Experiment {model_label1}  {year} with respect to {model_label2}'

    # Set the title above the subplots
    fig.suptitle(overall_title, fontsize=14, fontweight='bold')
    plt.subplots_adjust(hspace=0.5)
    
    filename = f"{outputfig}/Seasonal_Bias_Plot_{model_label1}_{var_name}_{statistic}_{year}.pdf"
    plt.savefig(filename, dpi = 300, format = 'pdf')
    plt.show()
                                                                
    # Write the data into a NetCDF file
    data_directory = outputdir
    data_filename = f"Seasonal_Bias_Data_{model_label1}_{var_name}_{statistic}_{year}.nc"
    data_path = os.path.join(data_directory, data_filename)

    data_array = xr.concat(results, dim='season')
    data_array.attrs = var1.attrs  # Copy attributes from var1 to the data_array
    data_array.attrs['statistic'] = statistic
    data_array.attrs['dataset1'] = model_label1
    data_array.attrs['dataset2'] = model_label2
    data_array.attrs['year'] = year

    data_array.to_netcdf(data_path)
    
    print(f"The seasonal bias plots have been saved to {outputfig}.")
    print(f"The seasonal bias data has been saved to {outputdir}.")
    

def compare_datasets_plev(dataset1, var_name, time_range, model_label):
    """
    Compare a dataset and plot the zonal bias for a selected model time range with respect to the ERA5 climatology from 2000-2020.

    Args:
        dataset1 (xarray.Dataset): The first dataset.
        var_name (str): The variable name to compare (examples: q, u, v, t)
        time_range (slice or str): The time range to select from the datasets. Should be a valid slice or a string in 'YYYY-MM-DD' format.
        data_era5 (xarray.Dataset or None): The ERA5 dataset for calculating the climatology. Set to None if not chosen.
        plot_latitude (bool): True to plot latitude on the x-axis, False to plot longitude.

    Returns:
        A zonal bias plot.
    """
    # Calculate the bias between dataset1 and dataset2
    reader_era5 = Reader(model="ERA5", exp="era5", source="monthly")
    data_era5 = reader_era5.retrieve(fix=True)
    data_era5 = data_era5.sel(time=slice('2000-01-01', '2020-12-31'))
    bias = dataset1[var_name].sel(time=time_range) - data_era5[var_name].mean(dim='time')

    # Get the pressure levels and coordinate values
    plev = bias['plev'].values
    coord_values = bias['lat'].values

    # Calculate the mean bias along the time axis
    mean_bias = bias.mean(dim='time')

    # Create the z-values for the contour plot
    coord_values_2d, plev_2d = np.meshgrid(coord_values, plev)
    z_values = np.mean(mean_bias, axis=2)

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 8))
    cax = ax.contourf(coord_values_2d, plev_2d, z_values, cmap='RdBu_r')
    ax.set_title(f'Bias of {var_name} ({data_era5[var_name].long_name})\n Experiment {model_label} with respect to ERA5 Climatology (2000-2020).\n Selected model time range: {time_range}.')
    ax.set_yscale('log')
    ax.set_ylabel('Pressure Level (Pa)')
    ax.set_xlabel('Latitude')
    ax.invert_yaxis()
    ax.set_xlim(-90, 90)

    # Add colorbar
    cbar = fig.colorbar(cax)
    cbar.set_label(f'{var_name} ({data_era5[var_name].units})')

    plt.show()
    # Save the pdf file
    filename = f"{outputfig}/Vertical_biases_{model_label}_{var_name}.pdf"
    plt.savefig(filename, dpi = 300, format = 'pdf')

        # Save the data into a NetCDF file
    filename = f"{outputdir}/Vertical_bias_{model_label}_{var_name}.nc"
    mean_bias.to_netcdf(filename)
    print(f"The vertical bias plots have been saved to {outputfig}.")
    print(f"The vertical bias data has been saved to {outputdir}.")
    
    
def plot_map_with_stats(dataset, var_name, time_range, model_label):
    """
    Plot a map of a chosen variable from a dataset with colorbar and statistics.

    Args:
        dataset (xarray.Dataset): The dataset containing the variable.
        var_name (str): The name of the variable to plot.
        time_range (slice or str): The time range to select from the dataset. Should be a valid slice or a string in 'YYYY-MM-DD' format.
    """
    # Calculate statistics
    var_data = dataset[var_name].sel(time=time_range).mean(dim='time')
    weights = np.cos(np.deg2rad(dataset.lat))
    weighted_data = var_data.weighted(weights)
    var_mean = weighted_data.mean(('lon', 'lat')).values.item()
    var_std = var_data.std().values.item()
    var_min = var_data.min().values.item()
    var_max = var_data.max().values.item()
    
#         # get the era 5 data for calculating the RMSE (serves as observation data)
#         reader_era5 = Reader(model="ERA5", exp="era5", source="monthly")
#         data_era5 = reader_era5.retrieve(fix=True)

#         # Calculate RMSE
#         obs_data = data_era5[var_name].mean(dim='time')  # Get the observed data for comparison
#         n = len(var_data.values)
#         rmse = np.sqrt(((obs_data - var_data) ** 2).mean().values.item())

    # Plot the map
    fig = plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())
    cmap = 'RdBu_r'  # Choose a colormap (reversed)
    im = ax.pcolormesh(var_data.lon, var_data.lat, var_data.values, cmap=cmap, transform=ccrs.PlateCarree())

    # Set plot title and axis labels
    ax.set_title(f'Map of {var_name} from {time_range} for {model_label}')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

    # Add continents and landlines
    ax.add_feature(cfeature.LAND, edgecolor='black', facecolor='gray')
    ax.add_feature(cfeature.COASTLINE)

    # Add colorbar (reversed)
    cbar = fig.colorbar(im, ax=ax, shrink=0.6, extend='both')
    cbar.set_label(f'{var_name} ({dataset[var_name].units})')
    cbar.set_ticks(np.linspace(var_data.max(), var_data.min(), num=11))

    # Display statistics below the plot
    stat_text = f'Mean: {var_mean:.2f} {dataset[var_name].units}    Std: {var_std:.2f}    Min: {var_min:.2f}    Max: {var_max:.2f}'
    ax.text(0.5, -0.3, stat_text, transform=ax.transAxes, ha='center')


    plt.show()

