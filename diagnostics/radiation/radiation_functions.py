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

def new_process_ceres_data(exp, source):
    """
    Extract CERES data for further analyis + create global means

    Args:
        exp:                            input experiment to be selected from the catalogue
        source:                         input source to be selected from the catalogue
        TOA_icon_gm:                    this is necessary to setting time axis to the same time axis as model output (modify if needed)

    Returns:
        TOA_ceres_clim_gm:
        TOA_ceres_ebaf_gm: 
        TOA_ceres_diff_samples_gm:
        reader_ceres_toa,
        TOA_ceres_clim,
        TOA_ceres_diff_samples: # returns the necessary ceres data for further evaluation
    """

    # reader_ceres_toa
    reader = Reader(model='CERES', exp=exp, source=source, regrid='r100')
    data = reader.retrieve()
    data['tnr']=data['mtntrf'] + data['mtnsrf']
    ceres = reader.regrid(data[['tnr','mtntrf', 'mtnsrf']])


    # limit to years that are complete
    complete = data.sel(time=slice('2001', '2021'))

    # time averages over each month and get the monthly anomaly
    clim = complete.groupby('time.month').mean('time')
    monthly_anomalies = complete.groupby('time.month') - clim

    # global mean
    clim_gm = reader.fldmean(clim)
    ceres_gm = reader.fldmean(ceres)
    anom_gm = reader.fldmean(monthly_anomalies)

    dictionary = {
        "model": "CERES",
        "exp": exp,
        "source": source,
        "gm": ceres_gm,
        "clim_gm": clim_gm,
        "anom_gm": anom_gm,
        "clim": clim,
        "anom": monthly_anomalies

    }

    return dictionary

def new_process_model_data(model, exp, source):
    """
    Extract Model output data for further analyis + create global means
    Example: TOA_ifs_4km_gm, reader_ifs_4km, data_ifs_4km, TOA_ifs_4km, TOA_ifs_4km_r360x180 = radiation_diag.process_model_data(model =  'IFS' , exp = 'tco2559-ng5-cycle3' , source = 'lra-r100-monthly')

    Args:
        model:                          input model to be selected from the catalogue
        exp:                            input experiment to be selected from the catalogue
        source:                         input source to be selected from the catalogue

    Returns:
        TOA_model_gm, reader_model, data_model, TOA_model, TOA_model_r360x180:       returns the necessary ceres data for further evaluation (xarrayDatSet, -Array, reader, regridded DataSet and Global                                                                                           means
    """

    reader = Reader(model=model, exp=exp, source=source, regrid='r100', fix=False)
    data = reader.retrieve(var=['mtntrf', 'mtnsrf'])
    data['tnr']=data['mtntrf'] + data['mtnsrf']
    gm = reader.fldmean(data)

    dictionary = {
        "model": model,
        "exp": exp,
        "source": source,
        "data": data,
        "gm": gm
    }

    return dictionary


def new_barplot_model_data(datasets, model_names, outputdir, outputfig, year=None):
    """
    Create Bar Plot with various models and CERES. Variables ttr and tsr are plotted to show imbalances.
    Default mean for CERES data is the whole time range.

    Args:
        datasets:      a list of xarrayDataSets that should be plotted. Chose the global means (TOA_$model_gm)
        model_names:   your desired naming for the plotting
        year:          the year for which the plot is generated (optional)

    Returns:
        A bar plot

    Example:

    .. code-block:: python

        datasets = [TOA_ceres_clim_gm, TOA_icon_gm, TOA_ifs_4km_gm, TOA_ifs_9km_gm]
        model_names = ['ceres', 'ICON', 'IFS 4.4 km', 'IFS 9 km']
        barplot_model_data(datasets, model_names, year = 2022)
    """

    #colors = ['red', 'blue', 'green', 'purple']  # Longwave (lw) in red, Shortwave (sw) in blue
    # Set a seaborn color palette
    sns.set_palette("pastel")
    #variables = ["mtntrf", "mtnsrf"]  # Fixed order: ttr (lw), tsr (sw)

    #global_means = {}

    data = pd.DataFrame({
        'Models': model_names,
        'mtntrf': [-datasets[i]["mtntrf"].mean().values.item() for i in range (0, len(datasets))],
        'mtnsrf': [datasets[i]["mtnsrf"].mean().values.item() for i in range (0, len(datasets))]
    })

    sns.set_palette("pastel")

    # Create a grouped bar plot
    ax = data.plot(x='Models', kind='bar', figsize=(8, 6))
    # Show the plot
    plt.legend(title='Groups')
    #ax.set_xticklabels( ('mtntrf', 'mtnsrf') )
    plt.xlabel('Model')
    plt.ylabel('Global mean ($W/m^2$)')
    plt.ylim(236, 250)
    if year is not None:
        plt.title(f"Global Mean TOA radiation for different models ({year}) (all CERES years from 2001 to 2021)")
    else:
        plt.title('Global Mean TOA radiation for different models') # (mean over all model times)')

    create_folder(folder=str(outputfig), loglevel='WARNING')

    filename = f"{outputfig}/BarPlot.pdf"
    plt.savefig(filename, dpi=300, format='pdf')
    plt.show()

    create_folder(folder=str(outputdir), loglevel='WARNING')

    # Save the data to a NetCDF file
    output_data = xr.Dataset(global_means)
    filename = f"{outputdir}/BarPlot.nc"
    output_data.to_netcdf(filename)

    print(f"Data has been saved to {outputdir}.")
    print(f"Plot has been saved to {outputfig}.")
