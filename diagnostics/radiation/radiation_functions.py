import os
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from cdo import Cdo
from aqua import Reader
from aqua.util import create_folder

cdo = Cdo(tempdir='./tmp/cdo-py')
tempdir = './tmp/cdo-py'
if not os.path.exists(tempdir):
    os.makedirs(tempdir)


def new_process_ceres_data(exp=None, source=None):
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


def new_process_model_data(model=None, exp=None, source=None):
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


def new_barplot_model_data(datasets=None, model_names=None, outputdir='./', outputfig='./', year=None, fontsize=14):
    """
    Create a grouped bar plot with various models and CERES data. Variables 'ttr' and 'tsr' are plotted to show imbalances.
    The default mean for CERES data is calculated over the entire time range.

    Args:
        datasets (list of xarray.DataSets): A list of xarray.DataSets to be plotted (e.g., global means).
        model_names (list of str):      Your desired naming for the plotting, corresponding to the datasets.
        outputdir (str, optional):      Directory where the output data will be saved (default is './').
        outputfig (str, optional):      Directory where the output figure will be saved (default is './').
        year (int, optional):           The year for which the plot is generated (optional).
        fontsize (int, optional):       Font size for labels and legends in the plot (default is 14).

    Returns:
        A bar plot showing the global mean radiation variables ('ttr' and 'tsr') for different models and CERES data.

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
