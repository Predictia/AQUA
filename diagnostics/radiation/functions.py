import os
import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import calendar
from cdo import Cdo
import cartopy.crs as ccrs
from matplotlib.legend_handler import HandlerTuple
from aqua import Reader
import matplotlib.gridspec as gridspec
from aqua.util import create_folder

cdo = Cdo(tempdir='./tmp/cdo-py')
tempdir='./tmp/cdo-py'
if not os.path.exists(tempdir):
    os.makedirs(tempdir)


def process_ceres_data(exp=None, source=None):
    """
    Function to extract CERES data for further analyis + create global means

    Args:
        exp (str):   Input experiment to be selected from the catalogue.
        source (str): Input source to be selected from the catalogue.

    Returns:
        dict: A dictionary containing the following information:
            - "model": "CERES".
            - "exp": Experiment name.
            - "source": Source name.
            - "gm": Global means of CERES data.
            - "clim_gm": Global means of climatology data.
            - "anom_gm": Global means of monthly anomalies data.
            - "clim": Climatology data.
            - "anom": Monthly anomalies data.
    """

    # reader_ceres_toa
    reader = Reader(model='CERES', exp=exp, source=source, regrid='r100')
    data = reader.retrieve()
    data['tnr'] = data['mtntrf'] + data['mtnsrf']
    ceres = reader.regrid(data[['tnr', 'mtntrf', 'mtnsrf']])

    # limit to years that are complete
    complete = data.sel(time=slice('2001', '2021'))

    # time averages over each month and get the monthly anomaly
    clim = complete.groupby('time.month').mean('time')
    
    monthly_anomalies = complete.groupby('time.month') - clim

    clim = clim.rename({'month': 'time'})

    # global mean
    clim_gm = reader.fldmean(clim)
    ceres_gm = reader.fldmean(ceres)
    anom_gm = reader.fldmean(monthly_anomalies)

    dictionary = {
        "model": "CERES",
        "exp": exp,
        "source": source,
        "data": ceres,
        "gm": ceres_gm,
        "clim_gm": clim_gm,
        "anom_gm": anom_gm,
        "clim": clim,
        "anom": monthly_anomalies

    }
    return dictionary

def process_model_data(model=None, exp=None, source=None):
    """
    Function to extract Model output data for further analysis and create global means.

    Args:
        model (str):   Input model to be selected from the catalogue.
        exp (str):     Input experiment to be selected from the catalogue.
        source (str):  Input source to be selected from the catalogue.

    Returns:
        dict: A dictionary containing the following information:
            - "model": Model name.
            - "exp": Experiment name.
            - "source": Source name.
            - "gm": Global means of model output data.
            - "data": Model output data.
    """

    reader = Reader(model=model, exp=exp, source=source,
                    regrid='r100', fix=False)
    data = reader.retrieve(var=['mtntrf', 'mtnsrf'])
    data['tnr'] = data['mtntrf'] + data['mtnsrf']
    gm = reader.fldmean(data)

    dictionary = {
        "model": model,
        "exp": exp,
        "source": source,
        "data": data,
        "gm": gm
    }

    return dictionary

def process_era5_data(exp, source):
    """
    Extract ERA5 data for further analyis
    Example: data_era5, reader_era5 = radiation_diag.process_era5_data(exp = "era5" , source = "monthly")

    Args:
        exp:                            input experiment to be selected from the catalogue
        source:                         input source to be selected from the catalogue

    Returns:
        data_era5, reader_era5:       returns the necessary ceres data for further evaluation (xarrayDatSet, reader)
    """

    reader_era5 = Reader(model="ERA5", exp=exp, source=source)
    data_era5 = reader_era5.retrieve()
    return data_era5, reader_era5

def gregory_plot(obs_data, obs_reader, obs_time_range, model_label_obs, model_list, reader_dict, outputdir, outputfig):
    """
    Create Gregory Plot with various models and an observational dataset (e.g., ERA5).

    Args:
        obs_data (xarray.Dataset): Xarray Dataset containing the observational data.
        obs_reader: corresponding reader object for the observational dataset
        obs_time_range (tuple): A tuple containing the start and end dates of the time range for the observational data.
                                Format: ('YYYY-MM-DD', 'YYYY-MM-DD')
        model_list (list): A list of models that should be plotted.
        reader_dict (dict): A dictionary mapping model names to corresponding reader objects.
        model_label_obs (str): Desired label for the observational data.

    Returns:
        A Gregory Plot.

    """

    # Create the plot and axes
    _, ax = plt.subplots()
    # Colors for the plots
    colors = ["orange", "gray", "dodgerblue", "yellow", "indigo", "violet"]

    # Plot the data for each model
    handles = []
    labels = []

    # Plot the data for observation
    obs_2t = obs_data["2t"].sel(time=slice(*obs_time_range))
    obs_tsr = obs_data["mtnsrf"].sel(time=slice(*obs_time_range))
    obs_ttr = obs_data["mtntrf"].sel(time=slice(*obs_time_range))

    obs_2t_resampled = obs_2t.resample(time="M").mean()
    obs_tsr_resampled = obs_tsr.resample(time="M").mean()
    obs_ttr_resampled = obs_ttr.resample(time="M").mean()

    # Plot the data
    line = ax.plot(
        obs_reader.fldmean(obs_2t_resampled) - 273.15,
        obs_reader.fldmean(obs_tsr_resampled) + obs_reader.fldmean(obs_ttr_resampled),
        marker="o",
        color="mediumseagreen",
        linestyle="-",
        markersize=3,
        label=model_label_obs,
    )
    handles.append(line[0])  # Append the line object itself
    labels.append(model_label_obs)

    for i, model in enumerate(model_list):
        model_name = model.lower()
        model_reader = reader_dict[model_name]
        model_data = model_reader.retrieve() #fix=True)
        model_color = colors[i % len(colors)]  # Rotate colors for each model

        ts = model_reader.fldmean(model_data["2t"].resample(time="M").mean()) - 273.15
        rad = model_reader.fldmean((model_data["mtnsrf"] + model_data["mtntrf"]).resample(time="M").mean())

        line, = ax.plot(
            ts,
            rad,
            color=model_color,
            linestyle="-",
            marker="o",
            markersize=5,
            label=model_name
        )
        handles.append(line)  # Append the line object itself
        labels.append(model_name)

        ax.plot(
            ts[0], rad[0],
            marker="*",
            color="black",
            linestyle="-",
            markersize=15,
        )
        ax.plot(
            ts[-1], rad[-1],
            marker="X",
            color="tab:red",
            linestyle="-",
            markersize=15,
        )

    # Set labels and title
    ax.set_xlabel("2m temperature [$^{\circ} C$]", fontsize=12)
    ax.set_ylabel("Net radiation TOA [Wm$^{-2}$]", fontsize=12)
    ax.set_title("Gregory Plot", fontsize=14)
    ax.legend(handles, labels + ["Start", "End"], handler_map={tuple: HandlerTuple(ndivide=None)})
    ax.text(0.5, -0.15, "Black stars indicate the first value of the dataseries\nRed X indicate the last value of the dataseries.",
            transform=ax.transAxes, fontsize=8, verticalalignment='top', horizontalalignment='center')
    ax.tick_params(axis="both", which="major", labelsize=10)
    ax.grid(True, linestyle="--", linewidth=0.5)

    
    
    # Save the data for each model to separate netCDF files
    for model in model_list:
        model_name = model.lower()
        model_reader = reader_dict[model_name]
        model_data = model_reader.retrieve() #fix=True)

        model_data_resampled = model_data.resample(time="M").mean()

        create_folder(folder=str(outputfig), loglevel='WARNING')
        create_folder(folder=str(outputdir), loglevel='WARNING')

        model_data_resampled.to_netcdf(f"{outputdir}/Gregory_Plot_{model_name}.nc")
        filename = f"{outputfig}/Gregory_Plot_{model_name}.pdf"
        plt.savefig(filename, dpi=300, format='pdf')
        
    plt.show()
    print(f"Data has been saved to {outputdir}.")
    print(f"Plot has been saved to {outputfig}.")


def barplot_model_data(datasets=None, model_names=None, outputdir='./', outputfig='./', year=None, fontsize=14):
    """
    Create a grouped bar plot with various models and CERES data. Variables 'mtntrf' and 'mtnsrf' are plotted to show imbalances.
    The default mean for CERES data is calculated over the entire time range.

    Args:
        datasets (list of xarray.DataSets): A list of xarray.DataSets to be plotted (e.g., global means).
        model_names (list of str):      Your desired naming for the plotting, corresponding to the datasets.
        outputdir (str, optional):      Directory where the output data will be saved (default is './').
        outputfig (str, optional):      Directory where the output figure will be saved (default is './').
        year (int, optional):           The year for which the plot is generated (optional).
        fontsize (int, optional):       Font size for labels and legends in the plot (default is 14).

    Returns:
        A bar plot showing the global mean radiation variables ('mtntrf' and 'mtnsrf') for different models and CERES data.

    Example:

    .. code-block:: python

        datasets = [ceres['clim_gm'], icon['gm'], ifs_4km['gm'], ifs_9km['gm']]
        model_names = ['ceres', 'icon', 'ifs 4.4 km', 'ifs 9 km']
        new_barplot_model_data(datasets, model_names, outputdir='test', outputfig='test')
    """
    # Set a seaborn color palette
    sns.set_palette("pastel")
    global_mean = {'Variables': ["mtntrf", "mtnsrf"]}
    for i in range(0, len(datasets)):
        global_mean.update({model_names[i]: [-datasets[i]["mtntrf"].mean(
        ).values.item(), datasets[i]["mtnsrf"].mean().values.item()]})
    global_mean = pd.DataFrame(global_mean)

    sns.set_palette("pastel")
    # Create a grouped bar plot
    ax = global_mean.plot(x='Variables', kind='bar', figsize=(8, 6))
    # Show the plot
    plt.legend(title='Datasets', fontsize=fontsize-2)
    plt.xlabel('Variables', fontsize=fontsize)
    plt.ylabel('Global mean ($W/m^2$)', fontsize=fontsize)
    plt.ylim(236, 250)
    plt.xticks(rotation=0, fontsize=fontsize-2)
    plt.yticks(fontsize=fontsize-2)
    if year is not None:
        plt.title(
            f"Global Mean TOA radiation for different models ({year}) (all CERES years from 2001 to 2021)", fontsize=fontsize+2)
    else:
        plt.title('Global Mean TOA radiation for different models',
                  fontsize=fontsize+2)  # (mean over all model times)')

    create_folder(folder=str(outputfig), loglevel='WARNING')

    filename = f"{outputfig}/BarPlot.pdf"
    plt.savefig(filename, dpi=300, format='pdf')
    plt.show()

    create_folder(folder=str(outputdir), loglevel='WARNING')

    # Save the data to a NetCDF file
    output_data = xr.Dataset(global_mean)
    filename = f"{outputdir}/BarPlot.nc"
    output_data.to_netcdf(filename)

    print(f"Data has been saved to {outputdir}.")
    print(f"Plot has been saved to {outputfig}.")

def plot_model_comparison_timeseries(models=None, linelabels=None, TOA_ceres_diff_samples_gm=None, TOA_ceres_clim_gm=None, outputdir='./', outputfig='./', ylim = 6.5):
                        
    """
    Create time series bias plot with various models and CERES, including the individual CERES years to show variabilities.
    Variables ttr, tsr, and tnr are plotted to show imbalances. Default mean for CERES data is the whole time range.

    Example:
    models = [TOA_icon_gm.squeeze(), TOA_ifs_4km_gm.squeeze(), TOA_ifs_9km_gm.squeeze()]
    linelabels = ['ICON 5 km', 'IFS 4.4 km', 'IFS 9 km']
    radiation_diag.plot_model_comparison_timeseries(models, linelabels, TOA_ceres_diff_samples_gm, TOA_ceres_clim_gm)

    Args:
        models: a list of xarrayDataSets of the respective models. You can use squeeze() to remove single-dimensional entries from an array
                to ensure that the input arrays have the same dimensions and shape.
        linelabels: your desired naming for the plotting (this will also be used in the filename).

    Returns:
        A plot to show the model biases for the whole time range.
    """
        
    fig, axes = plt.subplots(3, 1, figsize=(12, 8))
    
    #linecolors = plt.cm.get_cmap('tab10').colors
    # Set the Seaborn style (you can choose other styles if needed)
    sns.set_style("darkgrid")
    # Choose a Seaborn color palette (you can select a different one if needed)
    color_palette = sns.color_palette("Set1")  # Change "Set1" to your preferred palette
    # Get a list of colors from the palette
    linecolors = color_palette.as_hex()

    starting_year = int(models[0]["time.year"][0].values) if len(models[0].sel(time=str(models[0]["time.year"][0].values)).time) == 12 \
                    else int(models[0]["time.year"][0].values) + 1
    final_year = int(models[0]["time.year"][-1].values) if len(models[0].sel(time=str(models[0]["time.year"][-1].values)).time) == 12 \
                 else int(models[0]["time.year"][-1].values) + 1
    years = range(starting_year, final_year - 1)
    print(years)

    #if len(models[0].sel(time=models[0]["time.year"][0].values).time)==12:
    #    starting_year = int(models[0]["time.year"][0].values)
    #else:
    #    starting_year = int(models[0]["time.year"][0].values)+1
    
    #if len(models[0].sel(time=models[0]["time.year"][-1].values).time)==12:
    #    final_year = int(models[0]["time.year"][-1].values)
    #else:
    #    final_year = int(models[0]["time.year"][-1].values)+1

    #years = range(starting_year, final_year+1)

    xlim = [pd.to_datetime(str(models[0]["time.year"][0].values) +'-'+str(models[0]["time.month"][0].values)+'-'+str(models[0]["time.day"][0].values)), \
        pd.to_datetime(str(models[0]["time.year"][-1].values) +'-'+str(models[0]["time.month"][-1].values)+'-'+str(models[0]["time.day"][-1].values))]
    shading_data_list = [TOA_ceres_diff_samples_gm]

    for year in years:
        new_data = TOA_ceres_diff_samples_gm.assign_coords(time=models[0].sel(time=str(year)).time)
        shading_data_list.append(new_data)

    #shading_data = xr.concat(shading_data_list, dim='time')

    #long_time = np.append(shading_data['time'], shading_data['time'][::-1])
    
    for i, model in enumerate(models):
        ttr_diff = []  # Initialize an empty list to store the data for each year
        tsr_diff = []
        tnr_diff = []
        # Iterate through the years
        for year in years:
            diff_ttr = (model.mtntrf.sel(time=str(year)).squeeze() - TOA_ceres_clim_gm.squeeze().mtntrf.values)
            ttr_diff.append(diff_ttr)

            diff_tsr = (model.mtnsrf.sel(time=str(year)).squeeze() - TOA_ceres_clim_gm.squeeze().mtnsrf.values)
            tsr_diff.append(diff_tsr)

            diff_tnr = (model.tnr.sel(time=str(year)).squeeze() - TOA_ceres_clim_gm.squeeze().tnr.values)
            tnr_diff.append(diff_tnr)
        # Concatenate the data along the 'time' dimension
        ttr_diff = xr.concat(ttr_diff, dim='time')
        tsr_diff = xr.concat(tsr_diff, dim='time')
        tnr_diff = xr.concat(tnr_diff, dim='time')
        # Plot the data for the current model
        ttr_diff.plot(ax=axes[0], color=linecolors[i], label=linelabels[i], x='time')
        tsr_diff.plot(ax=axes[1], color=linecolors[i], label=linelabels[i], x='time')
        ttr_diff.plot(ax=axes[2], color=linecolors[i], label=linelabels[i], x='time')



    #axes[0].fill(long_time, np.append(shading_data['mtntrf'].min(dim='ensemble'), shading_data['mtntrf'].max(dim='ensemble')[::-1]), color='lightgrey', alpha=0.6, label='CERES individual years', zorder=0)
    
    axes[0].set_title('LW', fontsize=16)
    axes[0].set_xticklabels([])
    axes[0].set_xlabel('')
    axes[0].legend(loc="upper left", frameon=False, fontsize='medium', ncol=3)

    #axes[1].fill(long_time, np.append(shading_data['mtnsrf'].min(dim='ensemble'), shading_data['mtnsrf'].max(dim='ensemble')[::-1]), color='lightgrey', alpha=0.6, label='CERES individual years', zorder=0)
    
    axes[1].set_title('SW', fontsize=16)
    axes[1].set_xticklabels([])
    axes[1].set_xlabel('')

    #axes[2].fill(long_time, np.append(shading_data['tnr'].min(dim='ensemble'), shading_data['tnr'].max(dim='ensemble')[::-1]), color='lightgrey', alpha=0.6, label='CERES individual years', zorder=0)
    
    axes[2].set_title('net', fontsize=16)

    for i in range(3):
        axes[i].set_ylabel('$W/m^2$')
        axes[i].set_xlim(xlim)
        #axes[i].plot([pd.to_datetime('2020-01-01'), pd.to_datetime('2030-12-31')], [0, 0], color='black', linestyle=':')
        axes[i].set_ylim([-ylim, ylim])

    plt.suptitle('Global mean TOA radiation bias relative to CERES climatology - nextGEMS Cycle 3', fontsize=18)
    
    create_folder(folder=str(outputfig), loglevel='WARNING')

    filename = f"{outputfig}/TimeSeries_{linelabels}.pdf"
    plt.savefig(filename, dpi=300, format='pdf')
    plt.tight_layout()
    plt.show()

    create_folder(folder=str(outputdir), loglevel='WARNING')

    # Save the data for each model to separate netCDF files
    for i, model in enumerate(models):
        model_name = linelabels[i].replace(' ', '_').lower()
        model.to_netcdf(f"{outputdir}Timeseries_{linelabels}.nc")

    print(f"Data has been saved to {outputdir}.")
    print(f"Plot has been saved to {outputfig}.")
    
def plot_bias(data=None, iax=None, title=None, plotlevels=None, lower=None, upper=None, index=None):
    """
    Plot the bias of the data on a map. Bias is calculated as the difference between the data and a reference, with stippling applied to highlight data points falling within specified lower and upper thresholds.

    Args:
        data (xarray.DataArray): The model data to plot.
        iax (matplotlib.axes.Axes): The axes object to plot on.
        title (str): The title of the plot.
        plotlevels (int or list): The contour plot levels.
        lower (xarray.DataArray): Lower threshold for stippling.
        upper (xarray.DataArray): Upper threshold for stippling.
        index (int): The index of the data.

    Returns:
        A contour plot representing the bias of the data on the specified axes.
    """

    plot = data.plot(ax=iax,
                     transform=ccrs.PlateCarree(),
                     colors='RdBu_r',
                     linewidths=0.3,
                     levels=plotlevels,
                     add_colorbar=False,
                    )
    stipple_data = data.where(np.logical_and(data > lower.isel(month=index), data < upper.isel(month=index))) / data.where(np.logical_and(data > lower.isel(month=index), data < upper.isel(month=index)))
    #plot2 = stipple_data.plot.contourf(ax=iax, levels=[-10, 0, 10], hatches=["", "...."], add_colorbar=False, alpha=0, transform=ccrs.PlateCarree())

    iax.set_title(title, fontsize=small_fonts)
    # iax.set_title(data.label+' ('+str(len(data.ensemble))+')',fontsize=small_fonts)

    return plot


def plot_maps(TOA_model=None, var=None, model_label=None, TOA_ceres_diff_samples=None, TOA_ceres_clim=None, outputdir='./', outputfig='./', year='2020'):
    """
    Plot monthly bias maps of the specified variable and model using a Robinson projection.
    The bias is calculated as the difference between TOA model data and TOA CERES climatology.
    
    Args:
        TOA_model (xarray.DataArray): The TOA model data.
        var (str): The variable to plot ('tnr', 'mtnsrf', or 'mtntrf').
        model_label (str): Desired label for the model (used as the filename to save the figure).
        TOA_ceres_diff_samples (xarray.DataArray): The TOA CERES difference samples data.
        TOA_ceres_clim (xarray.DataArray): The TOA CERES climatology data.
        year (str, optional): The year to plot. Defaults to '2020'.

    Returns:
        Monthly bias plots of the chosen model, variable, and year.

    Example:
        plot_maps(TOA_model=TOA_ifs_4km_r360x180, TOA_ceres_diff_samples=TOA_ceres_diff_samples,
                  TOA_ceres_clim=TOA_ceres_clim, var='mtnsrf', model_label='Cycle 3 4.4 km IFS Fesom', year='2023')
        # Use the TOA_ifs_4km_r360x180 DataSet to ensure that the gridding is correct.

    """
    range_min = TOA_ceres_diff_samples.groupby('time.month').min(dim='ensemble')
    range_max = TOA_ceres_diff_samples.groupby('time.month').max(dim='ensemble')
    TOA_model = TOA_model.sel(time=year)
    if var == 'tnr':
        label = 'net'
    elif var == 'mtnsrf':
        label = 'SW'
    elif var == 'mtntrf':
        label = 'LW'

    if year == '2020':
        panel_1_off = True
    else:
        panel_1_off = False

    # what to use for significance testing
    # everything between these values will be considered not significant and hatched in the plot
    lower = range_min[var].rename({'time': 'month'})
    upper = range_max[var].rename({'time': 'month'})

    fig, ax = plt.subplots(4, 3, figsize=(22, 10), subplot_kw={'projection': ccrs.Robinson(central_longitude=180, globe=None)})
    plotlevels = np.arange(-50, 51, 10)
    global small_fonts
    small_fonts = 12
    axes = ax.flatten()

    for index in range(len(TOA_model.time)):  # some experiments have less than 12 months, draw fewer panels for those
            plot = plot_bias(TOA_model[var].sel(time=year).isel(time=index)-TOA_ceres_clim[var].isel(time=index),
                            iax=axes[index], title=calendar.month_name[index+1], plotlevels=plotlevels,
                            lower=lower, upper=upper, index=index)

    for axi in axes:
        axi.coastlines(color='black', linewidth=0.5)

    if panel_1_off:
        axes[0].remove()
    # common colorbar
    fig.subplots_adjust(right=0.95)
    cbar_ax = fig.add_axes([0.96, 0.3, 0.02, 0.4])  # [left, bottom, width, height]
    cbar = fig.colorbar(plot, cax=cbar_ax)
    cbar.ax.tick_params(labelsize=small_fonts)
    cbar.set_label('$W m^{-2}$', labelpad=-32, y=-.08, rotation=0)

    plt.suptitle(label+' TOA bias ' + model_label + ' ' + year + '\nrel. to CERES climatology (2001-2021)', fontsize=small_fonts*2)

    create_folder(folder=str(outputfig), loglevel='WARNING')

    filename = f"{outputfig}{label}_TOA_bias_maps_{year}_{model_label}.pdf"
    plt.savefig(filename, dpi=300, format='pdf')
    plt.show()
    
    create_folder(folder=str(outputdir), loglevel='WARNING')

    # Save the data to a netCDF file
    data = TOA_model[var].sel(time=year) - TOA_ceres_clim[var].isel(time=0)
    filename = f"{outputdir}{var}_TOA_bias_maps_{year}_{model_label}.nc"
    data.to_netcdf(filename)

    print(f"Data has been saved to {outputdir}.")
    print(f"Plot has been saved to {outputfig}.")


def plot_mean_bias(TOA_model=None, var=None, model_label=None, TOA_ceres_clim=None, start_year=None, end_year=None, outputdir='./', outputfig='./'):
    """
    Plot the mean bias of the data over the specified time range and relative to CERES climatology.

    Args:
        TOA_model (xarray.Dataset): The model TOA radiation data.
        var (str): The variable to plot (e.g., 'mtnsrf', 'mtntrf', 'tnr').
        model_label (str): The label for the model.
        TOA_ceres_clim (float): The CERES TOA radiation climatology.
        start_year (str): The start year of the time range for the model data.
        end_year (str): The end year of the time range for the model data.
        ceres_start_year (str, optional): The start year of the time range for the CERES data (optional).
        ceres_end_year (str, optional): The end year of the time range for the CERES data (optional).

    Returns:
        None. Displays the plot of the mean bias.

    Example:
        plot_mean_bias(TOA_model, 'mtnsrf', 'Cycle3_9km_IFS', TOA_ceres_clim, '2020', '2024', ceres_start_year='2000', ceres_end_year='2010')
    """
    plotlevels = np.arange(-50, 51, 10)
    # Calculate the mean bias over the specified time range
    mean_bias = (TOA_model[var].sel(time=slice(start_year, end_year)).mean(dim='time') - TOA_ceres_clim[var]).mean(dim='time')
    # Convert masked values to NaN
    mean_bias = mean_bias.where(~mean_bias.isnull(), np.nan)
    # Create the plot
    fig = plt.figure(figsize=(10, 6))
    gs = gridspec.GridSpec(2, 1, height_ratios=[10, 1], hspace=0.1)
    ax = plt.subplot(gs[0], projection=ccrs.PlateCarree())
    contour_plot = mean_bias.plot.contourf(ax=ax, transform=ccrs.PlateCarree(), cmap='RdBu_r', levels=20)
    ax.coastlines(color='black', linewidth=0.5)
    ax.gridlines(linewidth=0.5)
    ax.set_title(f'{var.upper()} Bias of the {model_label} climatology ({start_year} to {end_year})\n relative to the CERES climatology (2001-2021)', fontsize=14)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_xticks(np.arange(-180, 181, 30), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(-90, 91, 30), crs=ccrs.PlateCarree())
    ax.tick_params(axis='both', which='both', labelsize=10)
    ax.xaxis.set_ticklabels(['-180°', '-150°', '-120°', '-90°', '-60°', '-30°', '0°', '30°', '60°', '90°', '120°', '150°', '180°'])
    ax.yaxis.set_ticklabels(['-90°', '-60°', '-30°', '0°', '30°', '60°', '90°'])
    create_folder(folder=str(outputfig), loglevel='WARNING')

    filename = f"{outputfig}{var}_{model_label}_TOA_mean_biases_{start_year}_{end_year}_CERES.pdf"
    plt.savefig(filename, dpi=300, format='pdf')
    plt.show()

    create_folder(folder=str(outputdir), loglevel='WARNING')

    #Save the data to a netCDF file
    filename = f"{outputdir}{var}_{model_label}_TOA_mean_biases_{start_year}_{end_year}_CERES.nc"
    mean_bias.to_netcdf(filename)

    print(f"Data has been saved to {outputdir}.")
    print(f"Plot has been saved to {outputfig}.")

