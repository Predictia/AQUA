import os
import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import calendar
import dask
from cdo import Cdo
from scipy.stats import ttest_1samp
import cartopy.crs as ccrs
from matplotlib.legend_handler import HandlerTuple
from aqua import Reader
import matplotlib.gridspec as gridspec
from aqua.util import create_folder, add_cyclic_lon
from aqua.logger import log_configure

#cdo = Cdo(tempdir='./tmp/cdo-py')
#tempdir='./tmp/cdo-py'
#if not os.path.exists(tempdir):
#    os.makedirs(tempdir)

loglevel: str = 'WARNING'
logger = log_configure(log_level=loglevel, log_name='Radiation')

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

    starting_year = str(ceres["time.year"][0].values) if len(ceres.sel(time=str(ceres["time.year"][0].values)).time) == 12 \
                    else str(ceres["time.year"][0].values + 1)
    final_year = str(ceres["time.year"][-1].values) if len(ceres.sel(time=str(ceres["time.year"][-1].values)).time) == 12 \
                 else str(ceres["time.year"][-1].values -1)
    # limit to years that are complete
    complete = ceres.sel(time=slice(starting_year, final_year))

    # time averages over each month and get the monthly anomaly
    clim = complete.groupby('time.month').mean('time')
    monthly_anomalies = complete.groupby('time.month') - clim

    clim = clim.rename({'month': 'time'})
    # global mean
    clim_gm = reader.fldmean(clim)
    ceres_gm = reader.fldmean(ceres)
    anom_gm = reader.fldmean(monthly_anomalies)

    dictionary = {
        "model": "CERES".lower(),
        "exp": exp.lower(),
        "source": source.lower(),
        "data": complete,
        "gm": ceres_gm,
        "clim_gm": clim_gm,
        "anom_gm": anom_gm,
        "clim": clim,
        "anom": monthly_anomalies

    }
    return dictionary

def process_model_data(model=None, exp=None, source=None, fix=None):
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
    if fix is None:
        reader = Reader(model=model, exp=exp, source=source,
                    regrid='r100', fix = False)
    else: 
        reader = Reader(model=model, exp=exp, source=source,
                    regrid='r100', fix = True)
    data = reader.retrieve(var=['2t','mtntrf', 'mtnsrf'])
    data['tnr'] = data['mtntrf'] + data['mtnsrf']
    gm = reader.fldmean(data)

    dictionary = {
        "model": model.lower(),
        "exp": exp.lower(),
        "source": source.lower(),
        "data": data,
        "gm": gm
    }

    return dictionary

def gregory_plot(obs_data=None, models=None, obs_time_range=None, model_labels=None, obs_labels=None,  outputdir=None, outputfig=None, 
                 fontsize=14, markersize=3):
    """
    Create a Gregory Plot with various models and an observational dataset (e.g., ERA5).
    
    Args:
        obs_data (dict): Xarray Dataset containing the observational data.
        models (list): A list of models that should be plotted.
        obs_time_range (tuple, optional): A tuple containing the start and end dates of the time range for the observational data. 
            Format: ('YYYY-MM-DD', 'YYYY-MM-DD')
        model_labels (list, optional): Labels for the models. If not provided, default labels are used.
        obs_labels (str, optional): Desired label for the observational data.
        outputdir (str, optional): The directory to save the data files. 
        outputfig (str, optional): The directory to save the plot as a PDF.
        fontsize (int, optional): Font size for the plot labels and title.
        markersize (int, optional): Size of the markers in the plot.

    Returns:
        A Gregory Plot displaying the data for each model and the observational data.
    """
    # Create the plot and axes
    fig, ax = plt.subplots()
    fig.set_facecolor('white')
    # Colors for the plots
    colors = ["orange", "gray", "dodgerblue", "yellow", "indigo", "violet"]
    
    # Plot the data for each model
    handles = []
    labels = []

    models = models if isinstance(models, list) else [models]


    # Plot the data for observation
    if obs_time_range is None:
        dummy_model_gm = models[0]["gm"]
        starting_year = str(dummy_model_gm["time.year"][0].values) if len(dummy_model_gm.sel(time=str(dummy_model_gm["time.year"][0].values)).time) == 12 \
                        else str(dummy_model_gm["time.year"][0].values + 1)
        final_year = str(dummy_model_gm["time.year"][-1].values) if len(dummy_model_gm.sel(time=str(dummy_model_gm["time.year"][-1].values)).time) == 12 \
                    else str(dummy_model_gm["time.year"][-1].values -1)
        # limit to years that are complete
        obs_data_gm = obs_data["gm"].sel(time=slice(starting_year, final_year))
    else:
        obs_data_gm = obs_data["gm"].sel(time=slice(*obs_time_range))
    obs_2t_resampled = obs_data_gm["2t"].resample(time="M").mean()
    obs_tnr_resampled = obs_data_gm["tnr"].resample(time="M").mean()

    if obs_labels is None:
        obs_labels = obs_data["model"]+' '+obs_data["exp"]+' '+obs_data["source"] +', ('+starting_year+'-'+final_year+')'
    # Plot the data
    line = ax.plot(
        obs_2t_resampled - 273.15, obs_tnr_resampled,
        marker="o", color="mediumseagreen", linestyle="-", markersize=markersize, label=obs_labels)
    handles.append(line[0])  # Append the line object itself
    labels.append(obs_labels)

    for i, model in enumerate(models):
        model_name = model["model"]+' '+model["exp"]+' '+model["source"] if model_labels is None else model_labels[i]
        model_color = colors[i % len(colors)]  # Rotate colors for each model
        model_2t = model["gm"]["2t"].resample(time="M").mean() - 273.15
        model_tnr = model["gm"]["tnr"].resample(time="M").mean()
        
        line, = ax.plot(model_2t, model_tnr, color=model_color,
            linestyle="-", marker="o", markersize=5, label=model_name)
        handles.append(line)  # Append the line object itself
        labels.append(model_name)

        ax.plot(model_2t[0], model_tnr[0],
            marker="*", color="black", linestyle="-", markersize=markersize*5)
        ax.plot(model_2t[-1], model_tnr[-1],
            marker="X", color="tab:red", linestyle="-", markersize=markersize*5)
    # Set labels and title
    ax.set_xlabel("2m temperature [$^{\circ} C$]", fontsize=fontsize-2)
    ax.set_ylabel("Net radiation TOA [Wm$^{-2}$]", fontsize=fontsize-2)
    ax.set_title("Gregory Plot", fontsize=fontsize)
    ax.legend(handles, labels + ["Start", "End"], handler_map={tuple: HandlerTuple(ndivide=None)})
    # ax.text(0.5, -0.15, "Black stars indicate the first value of the dataseries\nRed X indicate the last value of the dataseries.",
    #         transform=ax.transAxes, fontsize=fontsize-6, verticalalignment='top', horizontalalignment='center')
    ax.tick_params(axis="both", which="major", labelsize=10)
    
    ax.grid(True, linestyle="--", linewidth=0.5)

    if outputdir is not None:
        create_folder(folder=str(outputdir), loglevel='WARNING')
        for model in models:
            start_date = str(model["data"]["time.year"][0].values) +'-'+str(model["data"]["time.month"][0].values)+'-'+str(model["data"]["time.day"][0].values)
            end_date = str(model["data"]["time.year"][-1].values) +'-'+str(model["data"]["time.month"][-1].values)+'-'+str(model["data"]["time.day"][-1].values)
            model_name = model["model"]+'_'+model["exp"]+'_'+model["source"] if model_labels is None else model_labels[i]
            model_data_resampled = model["gm"].resample(time="M").mean()
            model_data_resampled.to_netcdf(f"{outputdir}/gregory_plot_{model_name}_{start_date}_{end_date}.nc")
            logger.info(f"Data has been saved to {outputdir}.")

    # Save the data for each model to separate netCDF files
    if outputfig is not None:
        create_folder(folder=str(outputfig), loglevel='WARNING')
        for model in models:
            start_date = str(model["data"]["time.year"][0].values) +'-'+str(model["data"]["time.month"][0].values)+'-'+str(model["data"]["time.day"][0].values)
            end_date = str(model["data"]["time.year"][-1].values) +'-'+str(model["data"]["time.month"][-1].values)+'-'+str(model["data"]["time.day"][-1].values)
            model_name = model["model"]+'_'+model["exp"]+'_'+model["source"] if model_labels is None else model_labels[i]
            filename = f"{outputfig}/gregory_plot_{model_name}_{start_date}_{end_date}.pdf"
            plt.savefig(filename, dpi=300, format='pdf', bbox_inches="tight")
            logger.info(f"Plot has been saved to {outputfig}.")
    else:
        plt.show()
    

def boxplot_model_data(datasets=None, model_names=None, outputdir=None, outputfig=None, year=None, fontsize=14):
    """
    Create a boxplot with various models and CERES data. Variables 'mtntrf' and 'mtnsrf' are plotted to show imbalances.
    The default mean for CERES data is calculated over the entire time range.

    Args:
        datasets (list of xarray.DataSets): A list of xarray.DataSets to be plotted (e.g., global means).
        model_names (list of str): Your desired naming for the plotting, corresponding to the datasets.
        outputdir (str, optional): Directory where the output data will be saved. Default is None.
        outputfig (str, optional): Directory where the output figure will be saved. Default is None.
        year (int, optional): The year for which the plot is generated. Default is None.
        fontsize (int, optional): Font size for labels and legends in the plot. Default is 14.

    Returns:
        A boxplot showing the uncertainty of global mean radiation variables ('mtntrf' and 'mtnsrf') for different models and CERES data.
    """
    # Set a seaborn color palette
    sns.set_palette("pastel")

    # Initialize a dictionary to store data for the boxplot
    boxplot_data = {'Variables': [], 'Values': [], 'Datasets': []}

    model_names = [dataset["model"] + ' ' + dataset["exp"] + ' ' + dataset["source"] for dataset in datasets] if model_names is None else model_names

    for i in range(0, len(datasets)):
        # Extract values for 'mtntrf' and 'mtnsrf' from each dataset
        mtntrf_values = -datasets[i]["gm"]["mtntrf"].values.flatten()
        mtnsrf_values = datasets[i]["gm"]["mtnsrf"].values.flatten()

        # Update the boxplot_data dictionary
        boxplot_data['Variables'].extend(['mtntrf'] * len(mtntrf_values))
        boxplot_data['Variables'].extend(['mtnsrf'] * len(mtnsrf_values))
        boxplot_data['Values'].extend(mtntrf_values)
        boxplot_data['Values'].extend(mtnsrf_values)
        boxplot_data['Datasets'].extend([model_names[i]] * (len(mtntrf_values) + len(mtnsrf_values)))

    # Create a DataFrame from the boxplot_data dictionary
    boxplot_df = pd.DataFrame(boxplot_data)

    # Create a boxplot
    ax = sns.boxplot(x='Variables', y='Values', hue='Datasets', data=boxplot_df)

    # Add a legend outside the plot to the right side
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), title='Datasets', fontsize=fontsize-2)

    # Set labels and title
    plt.xlabel('Variables', fontsize=fontsize)
    plt.ylabel('Global mean ($W/m^2$)', fontsize=fontsize)
    #plt.ylim(230, 255)
    plt.xticks(rotation=0, fontsize=fontsize-2)
    plt.yticks(fontsize=fontsize-2)

    if year is not None:
        plt.title(
            f"Global Mean TOA radiation for different models ({year})", fontsize=fontsize+2)
    else:
        plt.title("Global Mean TOA radiation for different models", fontsize=fontsize+2)


    if outputdir is not None:
        create_folder(folder=str(outputdir), loglevel='WARNING')
        # Save the data to a NetCDF file
        output_data = xr.Dataset(global_mean)
        filename = f"{outputdir}/boxplot_mtntrf_mtnsrf_{'_'.join(model_names).replace(' ', '_').lower()}.nc"
        output_data.to_netcdf(filename)
        logger.info(f"Data has been saved to {outputdir}.")

    if outputfig is not None:
        create_folder(folder=str(outputfig), loglevel='WARNING')
        
        filename = f"{outputfig}/boxplot_mtntrf_mtnsrf_{'_'.join(model_names).replace(' ', '_').lower()}.pdf"
        plt.savefig(filename, dpi=300, format='pdf', bbox_inches="tight")
        logger.info(f"Plot has been saved to {outputfig}.")
    else:
        plt.show()

    

def plot_model_comparison_timeseries(models=None, linelabels=None, ceres=None, outputdir=None, outputfig=None, ylim = 6.5):
                        
    """
    Create time series bias plot with various models and CERES, including the individual CERES years to show variabilities.
    Variables ttr, tsr, and tnr are plotted to show imbalances. Default mean for CERES data is the whole time range.

    Args:
        models (list of xarray.DataSets): A list of xarray.DataSets of the respective models.
        linelabels (list of str): Your desired naming for the plotting (this will also be used in the filename).
        ceres (xarray.DataSet): The CERES data to be compared with the models.
        outputdir (str, optional): Directory where the output data will be saved. Default is None.
        outputfig (str, optional): Directory where the output figure will be saved. Default is None.
        ylim (float, optional): The limit for the y-axis in the plot. Default is 6.5.

    Returns:
        A plot to show the model biases for the whole time range.
    """
        
    fig, axes = plt.subplots(3, 1, figsize=(12, 8))
    # Set the Seaborn style (you can choose other styles if needed)
    sns.set_style("darkgrid")
    # Choose a Seaborn color palette (you can select a different one if needed)
    color_palette = sns.color_palette("Set1")  # Change "Set1" to your preferred palette
    # Get a list of colors from the palette
    linecolors = color_palette.as_hex()
    #linecolors = plt.cm.get_cmap('tab10').colors

    if models is None:
        raise ValueError("models cannot be None")
    elif isinstance(models, list):
        pass
    else:
        models = [models]
    if linelabels is None or isinstance(linelabels, list):
        pass
    else:
        linelabels = [linelabels]

    dummy_model_gm = models[0]["gm"]
    starting_year = int(dummy_model_gm["time.year"][0].values) if len(dummy_model_gm.sel(time=str(dummy_model_gm["time.year"][0].values)).time) == 12 \
                    else int(dummy_model_gm["time.year"][0].values) + 1
    final_year = int(dummy_model_gm["time.year"][-1].values) if len(dummy_model_gm.sel(time=str(dummy_model_gm["time.year"][-1].values)).time) == 12 \
                 else int(dummy_model_gm["time.year"][-1].values) -1
    years = range(starting_year, final_year+1)

    xlim = [pd.to_datetime(str(dummy_model_gm["time.year"][0].values) +'-'+str(dummy_model_gm["time.month"][0].values)+'-'+str(dummy_model_gm["time.day"][0].values)), \
        pd.to_datetime(str(dummy_model_gm["time.year"][-1].values) +'-'+str(dummy_model_gm["time.month"][-1].values)+'-'+str(dummy_model_gm["time.day"][-1].values))]
    
    if linelabels is None:
        linelabels = []
        for model in models:
            linelabels.append(model["model"]+' '+model["exp"]+' '+model["source"])

    for i, model in enumerate(models):
        ttr_diff = []  # Initialize an empty list to store the data for each year
        tsr_diff = []
        tnr_diff = []
        # Iterate through the years
        for year in years:
            ttr_diff.append(model["gm"].mtntrf.sel(time=str(year))- ceres['clim_gm'].mtntrf.values)
            tsr_diff.append(model["gm"].mtnsrf.sel(time=str(year))- ceres['clim_gm'].mtnsrf.values)
            tnr_diff.append(model["gm"].tnr.sel(time=str(year)) - ceres['clim_gm'].tnr.values)
        # Concatenate the data along the 'time' dimension
        ttr_diff = xr.concat(ttr_diff, dim='time')
        tsr_diff = xr.concat(tsr_diff, dim='time')
        tnr_diff = xr.concat(tnr_diff, dim='time')
        # Plot the data for the current model
        ttr_diff.plot(ax=axes[0], color=linecolors[i], label=linelabels[i], x='time')
        tsr_diff.plot(ax=axes[1], color=linecolors[i], label=linelabels[i], x='time')
        ttr_diff.plot(ax=axes[2], color=linecolors[i], label=linelabels[i], x='time')
    
    samples_tmp= []
    for year in range(int(ceres["data"]["time.year"][0].values), int(ceres["data"]["time.year"][-1].values)-1):
            # select year and assign (fake) time coordinates so that the differencing works
            samples_tmp.append(ceres["gm"].sel(time=str(year)).assign_coords(time=ceres["clim_gm"].time)- ceres["clim_gm"])
    TOA_ceres_diff_samples_gm = xr.concat(samples_tmp, dim='ensemble')
    shading_data_list = []
    for year in years:
        new_data = TOA_ceres_diff_samples_gm.assign_coords(time=dummy_model_gm.sel(time=str(year)).time)
        shading_data_list.append(new_data)
        shading_data = xr.concat(shading_data_list, dim='time')
        long_time = np.append(shading_data['time'], shading_data['time'][::-1])

    axes[0].fill(long_time, np.append(shading_data['mtntrf'].min(dim='ensemble'), shading_data['mtntrf'].max(dim='ensemble')[::-1]), 
                 color='lightgrey', alpha=0.6, label='ceres individual years', zorder=0)
    axes[0].set_title('LW', fontsize=16)
    axes[0].set_xticklabels([])
    axes[0].set_xlabel('')
    axes[0].legend(loc="upper left", frameon=False, fontsize='medium', ncol=3)

    axes[1].fill(long_time, np.append(shading_data['mtnsrf'].min(dim='ensemble'), shading_data['mtnsrf'].max(dim='ensemble')[::-1]),
                 color='lightgrey', alpha=0.6, label='ceres individual years', zorder=0)
    axes[1].set_title('SW', fontsize=16)
    axes[1].set_xticklabels([])
    axes[1].set_xlabel('')

    axes[2].fill(long_time, np.append(shading_data['tnr'].min(dim='ensemble'), shading_data['tnr'].max(dim='ensemble')[::-1]), 
                 color='lightgrey', alpha=0.6, label='ceres individual years', zorder=0)
    axes[2].set_title('net', fontsize=16)

    for i in range(3):
        axes[i].set_ylabel('$W/m^2$')
        axes[i].set_xlim(xlim)
        axes[i].plot(xlim , [0, 0], color='black', linestyle=':')
        axes[i].set_ylim([-ylim, ylim])

    #plt.suptitle('Global mean TOA radiation bias relative to CERES climatology - nextGEMS Cycle 3', fontsize=18)
    plt.suptitle('Global mean TOA radiation bias relative to CERES climatology', fontsize=18)
    
    plt.tight_layout()

    if outputdir is not None:
        create_folder(folder=str(outputdir), loglevel='WARNING')
        # Save the data for each model to separate netCDF files
        for i, model in enumerate(models):
            model_name = linelabels[i].replace(' ', '_').lower()
            start_date = str(model["data"]["time.year"][0].values) +'-'+str(model["data"]["time.month"][0].values)+'-'+str(model["data"]["time.day"][0].values)
            end_date = str(model["data"]["time.year"][-1].values) +'-'+str(model["data"]["time.month"][-1].values)+'-'+str(model["data"]["time.day"][-1].values)
            model["gm"].to_netcdf(f"{outputdir}timeseries_{model_name}_{start_date}_{end_date}.nc")
        logger.info(f"Data has been saved to {outputdir}.")

    if outputfig is not None:
        create_folder(folder=str(outputfig), loglevel='WARNING')
        all_labels = '_'.join(linelabels).replace(' ', '_').lower()
        filename = f"{outputfig}/timeseries_{all_labels}.pdf"
        plt.savefig(filename, dpi=300, format='pdf', bbox_inches="tight")
        logger.info(f"Plot has been saved to {outputfig}.")
    else:
        plt.show()
       

    
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


def plot_maps(model=None, var=None, year=None, model_label=None,  ceres=None, outputdir=None, outputfig=None):
    """
    Plot monthly bias maps of the specified variable and model using a Robinson projection.
    The bias is calculated as the difference between TOA model data and TOA CERES climatology.
    
    Args:
        model (xarray.DataArray): The TOA model data.
        var (str): The variable to plot ('tnr', 'mtnsrf', or 'mtntrf').
        year (int, optional): The year to plot. Defaults to None.
        model_label (str, optional): Desired label for the model (used as the filename to save the figure). Defaults to None.
        ceres (xarray.DataArray): The TOA CERES data to be compared with the model.
        outputdir (str, optional): Directory where the output data will be saved. Defaults to None.
        outputfig (str, optional): Directory where the output figure will be saved. Defaults to None.

    Returns:
        Monthly bias plots of the chosen model, variable, and year.


    """
    samples_tmp= []
    for _year in range(int(ceres["data"]["time.year"][0].values), int(ceres["data"]["time.year"][-1].values)-1):
            # select year and assign (fake) time coordinates so that the differencing works
            samples_tmp.append(ceres["data"].sel(time=str(_year)).assign_coords(time=ceres["clim"].time)- ceres["clim"])
    TOA_ceres_diff_samples = xr.concat(samples_tmp, dim='ensemble')
    TOA_ceres_diff_samples = TOA_ceres_diff_samples.assign_coords(ensemble=range(len(samples_tmp)))
    range_min = TOA_ceres_diff_samples.groupby('time').min(dim='ensemble') #time.month
    range_max = TOA_ceres_diff_samples.groupby('time').max(dim='ensemble')
    if year is None:
        year = int(model["data"]["time.year"][0].values)

    label_dict = {'tnr': 'net', 'mtnsrf': 'SW', 'mtntrf': 'LW'}
    label = label_dict.get(var, None)

    model_label = model["model"]+'_'+model["exp"]+'_'+model["source"] if model_label is None else model_label

    # what to use for significance testing
    # everything between these values will be considered not significant and hatched in the plot
    lower = range_min[var].rename({'time': 'month'})
    upper = range_max[var].rename({'time': 'month'})

    fig, ax = plt.subplots(4, 3, figsize=(22, 10), subplot_kw={'projection': ccrs.Robinson(central_longitude=180, globe=None)})
    global_mean_bias = model["gm"][var].mean().values-ceres["clim_gm"][var].mean().values
    plotlevels = np.arange(-50+global_mean_bias, 51+global_mean_bias, 10)
    global small_fonts
    small_fonts = 12
    axes = ax.flatten()

    data = model["gm"].sel(time=str(year))
    for index in range(len(data.time)):  # some experiments have less than 12 months, draw fewer panels for those
            plot = plot_bias(data [var].isel(time=index)-ceres["clim"][var].isel(time=index),
                            iax=axes[index], title=calendar.month_name[index+1], plotlevels=plotlevels,
                            lower=lower, upper=upper, index=index)

    for axi in axes:
        axi.coastlines(color='black', linewidth=0.5)

    # common colorbar
    fig.subplots_adjust(right=0.95)
    cbar_ax = fig.add_axes([0.96, 0.3, 0.02, 0.4])  # [left, bottom, width, height]
    cbar = fig.colorbar(plot, cax=cbar_ax)
    cbar.ax.tick_params(labelsize=small_fonts)
    cbar.set_label('$W m^{-2}$', labelpad=-32, y=-.08, rotation=0)

    plt.suptitle(label+' TOA bias ' + model_label + ' ' + str(year) + '\nrel. to CERES climatology (2001-2021)', fontsize=small_fonts*2)
    plt.tight_layout()

    if outputdir is not None:
        create_folder(folder=str(outputdir), loglevel='WARNING')
        # Save the data to a netCDF file
        data = model["data"][var].sel(time=str(year)) - ceres["clim"][var].isel(time=0)
        filename = f"{outputdir}toa_bias_maps_{var}_{year}_{model_label}.nc"
        data.to_netcdf(filename)
        logger.info(f"Data has been saved to {outputdir}.")

    if outputfig is not None:
        create_folder(folder=str(outputfig), loglevel='WARNING')
        filename = f"{outputfig}toa_bias_maps_{label}_{year}_{model_label}.pdf"
        plt.savefig(filename, dpi=300, format='pdf', bbox_inches="tight")
        logger.info(f"Plot has been saved to {outputfig}.") 
    else:
        plt.show()



def plot_mean_bias(model=None, var=None, model_label=None, ceres=None, start_year=None, end_year=None, outputdir=None, outputfig=None, seasons=False, quantiles=False):
    """
    Plot the mean bias of the data over the specified time range and relative to CERES climatology.

    Args:
        model (xarray.Dataset): The model TOA radiation data.
        var (str): The variable to plot (e.g., 'mtnsrf', 'mtntrf', 'tnr').
        model_label (str): The label for the model.
        ceres (float): The CERES TOA radiation climatology.
        start_year (str): The start year of the time range for the model data.
        end_year (str): The end year of the time range for the model data.
        outputdir (str, optional): Directory where the output data will be saved. Defaults to None.
        outputfig (str, optional): Directory where the output figure will be saved. Defaults to None.
        seasons (bool, optional): If True, generate plots for each season (DJF, MAM, JJA, SON). Defaults to False.

    Returns:
        None. Displays the plot of the mean bias.
    """
    if start_year is None or end_year is None:

        start_year = str(model["data"]["time.year"][0].values) if len(model["data"].sel(time=str(model["data"]["time.year"][0].values)).time) == 12 \
                    else str(model["data"]["time.year"][0].values + 1)
        end_year = str(model["data"]["time.year"][-1].values) if len(model["data"].sel(time=str(model["data"]["time.year"][-1].values)).time) == 12 \
                    else str(model["data"]["time.year"][-1].values -1)
    if seasons:
        # Generate plots for each season
        season_months = {
            'DJF': [12, 1, 2],
            'MAM': [3, 4, 5],
            'JJA': [6, 7, 8],
            'SON': [9, 10, 11],
        }

        # Create a single subplot for all seasons
        fig, axs = plt.subplots(2, 2, subplot_kw={'projection': ccrs.PlateCarree()}, figsize=(15, 10))
        axs = axs.flatten()

        for i, (season, months) in enumerate(season_months.items()):
            # Calculate the mean bias over the specified time range and months
            if season == 'DJF':
                # Include December from the last year only if it's available
                if 12 in months:
                    months = [12] + months[1:]
                    years = np.arange(int(start_year) - 1, int(end_year) + 1)
                else:
                    years = np.arange(int(start_year), int(end_year) + 1)
            else:
                years = np.arange(int(start_year), int(end_year) + 1)

            #print(f"Season: {season}, Months: {months}, Years: {years}")

            # Extract model data for the specific season
            model_season_data = (
                model["data"][var]
                .sel(time=(model["data"]["time.month"].isin(months)) & (model["data"]["time.year"].isin(years)))
                .mean(dim='time')
            )

            #print(model_season_data)

            # Convert masked values to NaN
            model_season_data = model_season_data.where(~model_season_data.isnull(), np.nan)
                                    
            # Extract CERES climatology for the specific season
            ceres_time_month = ceres["clim"]["time"]
            ceres_seasonal_climatology = ceres["clim"][var].sel(
                time=ceres_time_month[ceres_time_month.isin(months)]
            ).mean(dim='time')
            
            # Calculate the mean bias over the specified time range and months
            mean_bias = model_season_data - ceres_seasonal_climatology

            # Add cyclic longitude
            mean_bias = add_cyclic_lon(mean_bias)

            model_label = model["model"]+'_'+model["exp"]+'_'+model["source"] if model_label is None else model_label
            
            model_label_season = f'{model_label}_{season}'
            
            # #debugging part:
            # print('mean bias data')
            # print(mean_bias)
            # print('model season data coordinates')
            # print(model_season_data.coords)
            # print('ceres seasonal climatology coordinates')
            # print(ceres_seasonal_climatology.coords)
            
            # Plot on the current subplot
            contour_plot = mean_bias.plot.contourf(ax=axs[i], transform=ccrs.PlateCarree(), cmap='RdBu_r', levels=20,
                                                   add_colorbar=False, add_labels=False, extend='both')

            # Explicitly convert masked elements to NaN for warning suppression
            contour_plot.collections[0].set_edgecolor("face")
            
            axs[i].coastlines(color='black', linewidth=0.5)
            axs[i].gridlines(linewidth=0.5)
            axs[i].set_title(f'{var.upper()} bias ({season} of the {model_label}\n climatology {start_year} to {end_year})\n relative to the CERES climatology (2001-2021)',
                             fontsize=12)
            axs[i].set_xlabel('Longitude')
            axs[i].set_ylabel('Latitude')
            axs[i].set_xticks(np.arange(-180, 181, 30), crs=ccrs.PlateCarree())
            axs[i].set_yticks(np.arange(-90, 91, 30), crs=ccrs.PlateCarree())
            axs[i].tick_params(axis='both', which='both', labelsize=8)
            axs[i].xaxis.set_ticklabels(
                ['-180°', '-150°', '-120°', '-90°', '-60°', '-30°', '0°', '30°', '60°', '90°', '120°', '150°', '180°'])
            axs[i].yaxis.set_ticklabels(['-90°', '-60°', '-30°', '0°', '30°', '60°', '90°'])
            
#             ################################
#             #investigating quantiles
            
#             # Calculate quantiles (e.g., 5th and 95th percentiles)
           
#             try:
#                 quantiles = mean_bias.quantile([0.05, 0.95], dim=['lat','lon'])
#             except ValueError as e:
#                 print(f"Error calculating quantiles: {e}")
#                 print("Dimensions of mean_bias:")
#                 print(mean_bias.dims)
#                 print("Shape of mean_bias:")
#                 print(mean_bias.shape)
#                 raise ValueError(f"Error calculating quantiles: {e}")
            
#             print("Quantiles Shape:", quantiles.shape)
#             print("Quantiles Values:")
#             print(quantiles)
#             print('quantile coords:')
#             print(quantiles.coords)

             
#             axs[i].contourf(model_season_data.lon, model_season_data.lat, quantiles.sel(quantile=0.05).squeeze().values,
#                 levels=1, colors='none', hatches=['.'], extend='both', transform=ccrs.PlateCarree())
#             axs[i].contourf(model_season_data.lon, model_season_data.lat, quantiles.sel(quantile=0.95).squeeze().values,
#                 levels=1, colors='none', hatches=['.'], extend='both', transform=ccrs.PlateCarree())

#             plt.figure(figsize=(10, 6))
#             plt.title('Quantile 0.05')
#             plt.colorbar()
#             plt.show()

#             plt.figure(figsize=(10, 6))
#             plt.imshow(quantiles.sel(quantile=0.95).squeeze().values, extent=[model_season_data.lon.min(), model_season_data.lon.max(), model_season_data.lat.min(), model_season_data.lat.max()])
#             plt.title('Quantile 0.95')
#             plt.colorbar()
#             plt.show()

#             ################################
            
        # Add a colorbar for the entire figure
        cbar_ax = fig.add_axes([0.2, 0.08, 0.6, 0.02])
        cbar = fig.colorbar(contour_plot, cax=cbar_ax, orientation='horizontal',
                            label=f'{var.lower()} bias [' + mean_bias.units + ']')
        # Explicitly convert masked elements to NaN for warning suppression
        contour_plot.collections[0].set_edgecolor("face")

        if outputdir is not None:
            create_folder(folder=str(outputdir), loglevel='WARNING')
            # Save the data to a netCDF file
            ceres_model_name = ceres["model"] + '_' + ceres["exp"] + '_' + ceres["source"]
            filename = f"{outputdir}toa_mean_biases_{var}_{model_label}_{start_year}_{end_year}_{ceres_model_name}_seasons.pdf"
            plt.savefig(filename, dpi=300, format='pdf', bbox_inches="tight")
            logger.info(f"Data has been saved to {outputdir}.")

        if outputfig is not None:
            create_folder(folder=str(outputfig), loglevel='WARNING')
            ceres_model_name = ceres["model"] + '_' + ceres["exp"] + '_' + ceres["source"]
            filename = f"{outputfig}toa_mean_biases_{var}_{model_label}_{start_year}_{end_year}_{ceres_model_name}_seasons.pdf"
            plt.savefig(filename, dpi=300, format='pdf', bbox_inches="tight")
            logger.info(f"Plot has been saved to {outputfig}.")
        else:
            plt.show()
            
    ################################################################################################################        
     
    else:
        # Extract model data for the entire time series
        model_data = model["data"][var].sel(time=slice(str(start_year), str(end_year)))

        mean_bias = (model_data.mean(dim='time') - ceres["clim"][var]).mean(dim='time')
        # Convert masked values to NaN
        mean_bias = mean_bias.where(~mean_bias.isnull(), np.nan)
        mean_bias = add_cyclic_lon(mean_bias)

        model_label = model["model"]+'_'+model["exp"]+'_'+model["source"] if model_label is None else model_label

        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()}, figsize=(8, 6))

        # Plot mean biases
        contour_plot = mean_bias.plot.contourf(ax=ax, transform=ccrs.PlateCarree(), cmap='RdBu_r', levels=20,
                                               add_colorbar=False, add_labels=False, extend='both')

        ########################### significance part testing
        try:
            # Initialize an array to store the significance mask for each month
            monthly_significance_masks = []

            for month in range(1, 13):
                # Extract model data for the specific month
                model_month_data = model_data.sel(time=model_data['time.month'] == month)

                # Calculate the mean bias for the specific month
                mean_bias_month = (model_month_data.mean(dim='time') - ceres["clim"][var].sel(time=month)).mean(dim='time')

                # Calculate quantiles for the specific month
                q05 = mean_bias_month.quantile(0.05, dim=['lat', 'lon'])
                q95 = mean_bias_month.quantile(0.95, dim=['lat', 'lon'])

                # Stippling for points within the 95% confidence interval for the specific month
                monthly_significance_mask = (mean_bias_month >= q05) & (mean_bias_month <= q95)
                monthly_significance_masks.append(monthly_significance_mask)

                # Stipple points on the plot
                lons, lats = np.meshgrid(mean_bias_month['lon'], mean_bias_month['lat'])
                ax.scatter(lons[monthly_significance_mask], lats[monthly_significance_mask], marker='.', color='black', s=.1, alpha=0.7, transform=ccrs.PlateCarree())

            # Combine the monthly significance masks to check for consistency across months
            combined_significance_mask = np.all(monthly_significance_masks, axis=0)

        except ValueError as e:
            print(f"Error calculating quantiles: {e}")
        
        ###############################################

        fig.subplots_adjust(bottom=0.25, top=0.9, left=0.05, right=0.95,
                             wspace=0.1, hspace=0.5)
        cbar_ax = fig.add_axes([0.2, 0.15, 0.6, 0.02])
        try:
            fig.colorbar(contour_plot, cax=cbar_ax, orientation='horizontal',
                        label=mean_bias.long_name+' bias ['+mean_bias.units+']')
        except AttributeError:
            fig.colorbar(contour_plot, cax=cbar_ax, orientation='horizontal')

        ax.coastlines(color='black', linewidth=0.5)
        ax.gridlines(linewidth=0.5)
        ax.set_title(f'{var.upper()} bias of the {model_label.replace("_", " ")} climatology ({start_year} to {end_year})\n relative to the CERES climatology (2001-2021)', fontsize=14)
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_xticks(np.arange(-180, 181, 30), crs=ccrs.PlateCarree())
        ax.set_yticks(np.arange(-90, 91, 30), crs=ccrs.PlateCarree())
        ax.tick_params(axis='both', which='both', labelsize=10)
        ax.xaxis.set_ticklabels(['-180°', '-150°', '-120°', '-90°', '-60°', '-30°', '0°', '30°', '60°', '90°', '120°', '150°', '180°'])
        ax.yaxis.set_ticklabels(['-90°', '-60°', '-30°', '0°', '30°', '60°', '90°'])

        if outputdir is not None:
            create_folder(folder=str(outputdir), loglevel='WARNING')
            # Save the data to a netCDF file
            ceres_model_name = ceres["model"]+'_'+ceres["exp"]+'_'+ceres["source"]
            filename = f"{outputdir}toa_mean_biases_{var}_{model_label}_{start_year}_{end_year}_{ceres_model_name}.nc"
            mean_bias.to_netcdf(filename)
            logger.info(f"Data has been saved to {outputdir}.")

        if outputfig is not None:
            create_folder(folder=str(outputfig), loglevel='WARNING')
            ceres_model_name = ceres["model"]+'_'+ceres["exp"]+'_'+ceres["source"]
            filename = f"{outputfig}toa_mean_biases_{var}_{model_label}_{start_year}_{end_year}_{ceres_model_name}.pdf"
            plt.savefig(filename, dpi=300, format='pdf', bbox_inches="tight")
            logger.info(f"Plot has been saved to {outputfig}.")
        else:
            plt.show()


