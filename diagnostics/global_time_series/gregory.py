"""Gregory plot module."""
import matplotlib.pyplot as plt
from aqua import Reader
from aqua.logger import log_configure
from aqua.exceptions import NotEnoughDataError, NoDataError


def plot_gregory(model, exp, source,
                 reader_kw={}, plot_kw={},
                 regrid=None, freq=None,
                 ts_name='2t', toa_name=['mtnlwrf', 'mtnswrf'],
                 loglevel='WARNING', **kwargs):
    """Plot global mean SST against net radiation at TOA.

    Parameters:
        model (str): Model ID.
        exp (str): Experiment ID.
        source (str): Source ID.
        reader_kw (dict): Additional keyword arguments passed to the `aqua.Reader`.
        plot_kw (dict): Additional keyword arguments passed to the plotting function.
        regrid (str): Optional regrid resolution. Default is None.
        freq (str): frequency for timmean applied to data, default is None.
        ts (str): variable name for 2m temperature, default is '2t'.
        toa (list): list of variable names for net radiation at TOA, default is ['mtnlwrf', 'mtnswrf'].
        loglevel (str): Logging level. Default is WARNING.

    Raises:
        NotEnoughDataError: if there are not enough data to plot.
        NoDataError: if the variable is not found.
    """
    logger = log_configure(loglevel, 'Gregory plot')

    retrieve_list = [ts_name] + toa_name
    logger.debug(f"Retrieving {retrieve_list}")

    try:
        reader = Reader(model, exp, source, regrid=regrid, loglevel=loglevel, **reader_kw)
        data = reader.retrieve(var=retrieve_list)
    except Exception as e:
        logger.error(f"Error: {e}")
        raise NoDataError(f"Could not retrieve data for {model}-{exp}. No plot will be drawn.") from e

    if len(data.time) < 2:
        raise NotEnoughDataError("There are not enough data to proceed. Global time series diagnostic requires at least two data points.")

    if freq:
        logger.debug(f"Resampling data to {freq}")
        data = reader.timmean(data=data, freq=freq)
    else:
        logger.warning("No frequency given, be aware that the data is not resampled for the monthly plot.")
    if regrid:
        logger.debug(f"Regridding data to {regrid}")
        data = reader.regrid(data)

    try:
        ts = reader.fldmean(data[ts_name]).values - 273.15
        toa = reader.fldmean(data[toa_name[0]] + data[toa_name[1]]).values
    except Exception as e:
        logger.error(f"Error: {e}")
        raise NoDataError(f"Could not retrieve data for {model}-{exp}. No plot will be drawn.") from e

    # Preparing data for annual mean
    data = reader.timmean(data=data, freq='YS')

    if len(data.time) < 2:
        raise NotEnoughDataError("There are not enough data to proceed with annual Gregory plot.")

    ts_annual = reader.fldmean(data[ts_name]).values - 273.15
    toa_annual = reader.fldmean(data[toa_name[0]] + data[toa_name[1]]).values

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    # Plot monthly data
    ax1.axhline(0, color="k")
    ax1.plot(ts, toa, marker=".", **plot_kw, label="Monthly Mean", lw=0.5, alpha=0.8)
    ax1.plot(ts[0], toa[0], marker=">", color="tab:green", label="First Time-step")
    ax1.plot(ts[-1], toa[-1], marker="<", color="tab:red", label="Last Time-step")
    ax1.set_xlabel("2m temperature / C")
    ax1.set_ylabel(r"Net radiation TOA / $\rm Wm^{-2}$")
    ax1.grid(True)  # Add grid in the background
    ax1.legend()  # Add legend

    # Plot annual data
    ax2.axhline(0, color="k", lw=0.7)
    ax2.plot(ts_annual, toa_annual, marker=".", color="#000066", lw=1.1, label="Annual Mean")
    ax2.plot(ts_annual[0], toa_annual[0], marker=">", color="tab:green")
    ax2.plot(ts_annual[-1], toa_annual[-1], marker="<", color="tab:red")
    ax2.set_xlabel("2m temperature / C")
    ax2.grid(True)  # Add grid in the background
    ax2.legend()  # Add legend

    plt.tight_layout()  # Adjust spacing between subplots

    # Add model and experiment to title
    title = "Gregory plot"
    title += f"\n{model} {exp}"

    plt.subplots_adjust(top=0.85)
    fig.suptitle(title)

    return fig


def get_reference_gregory(ts_name='2t', toa_name=['mtnlwrf', 'mtnswrf'],
                          ts_ref={'model': 'ERA5', 'exp': 'era5', 'source': 'monthly'},
                          toa_ref={'model': 'ERA5', 'exp': 'era5', 'source': 'monthly'},
                          startdate='1980-01-01', enddate='2010-12-31', loglevel='WARNING'):
    """Retrieve reference data for Gregory plot.

    Parameters:
        ts_name (str): variable name for 2m temperature, default is '2t'.
        toa_name (list): list of variable names for net radiation at TOA, default is ['mtnlwrf', 'mtnswrf'].
        ts_ref (dict): dictionary with model, exp and source for 2m temperature, default is {'model': 'ERA5', 'exp': 'era5', 'source': 'monthly'}.
        toa_ref (dict): dictionary with model, exp and source for net radiation at TOA, default is {'model': 'ERA5', 'exp': 'era5', 'source': 'monthly'}.
        startdate (str): start date for reference data, default is '1980-01-01'.
        enddate (str): end date for reference data, default is '2010-12-31'.

    Returns:
        dict: dictionary with 2m temperature and net radiation at TOA for reference data.
              A center value is given together with the standard deviation for the selected period.
    """
    logger = log_configure(loglevel, 'get_reference_gregory')

    # Retrieve and evaluate ts:
    reader_ts = Reader(ts_ref['model'], ts_ref['exp'], ts_ref['source'],
                       startdate=startdate, enddate=enddate, loglevel=loglevel)
    data_ts = reader_ts.retrieve(var=ts_name)
    data_ts = data_ts[ts_name]
    data_ts = reader_ts.timmean(data_ts, freq='YS')
    data_ts = reader_ts.fldmean(data_ts)

    logger.debug("Evaluating 2m temperature")

    ts_std = data_ts.std().values
    ts_mean = data_ts.mean().values

    # Retrieve and evaluate toa:
    reader_toa = Reader(toa_ref['model'], toa_ref['exp'], toa_ref['source'],
                        startdate=startdate, enddate=enddate, loglevel=loglevel)
    data_toa = reader_toa.retrieve(var=toa_name)
    data_toa = data_toa[toa_name[0]] + data_toa[toa_name[1]]
    data_toa = reader_toa.timmean(data_toa, freq='YS')
    data_toa = reader_toa.fldmean(data_toa)

    logger.debug("Evaluating net radiation at TOA")

    toa_std = data_toa.std().values
    toa_mean = data_toa.mean().values

    return {'ts': {'mean': ts_mean, 'std': ts_std},
            'toa': {'mean': toa_mean, 'std': toa_std}}
