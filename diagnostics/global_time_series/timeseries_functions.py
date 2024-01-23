"""Functions for global time series diagnostics.
"""
import matplotlib.pyplot as plt
from aqua import Reader
from aqua.logger import log_configure
from aqua.exceptions import NotEnoughDataError, NoObservationError, NoDataError
from aqua.util import eval_formula

__all__ = [
    "plot_timeseries",
    "plot_gregory",
]


def get_reference_data(varname, formula=False, model='ERA5', exp='era5', source='monthly',
                       sel=None, resample=None, regrid=None, loglevel='WARNING'):
    """
    Get reference data for a given variable.
    Default is ERA5 monthly data.

    Parameters:
        varname (str or list): Variable(s) name to retrieve.
        formula (bool, opt): If True, try to derive the variable from other variables.
        model (str, opt): Model ID. Default is ERA5.
        exp (str, opt): Experiment ID. Default is era5.
        source (str, opt): Source ID. Default is monthly.
        sel (dict, opt): Selection dictionary. Default is None.
        resample (str, opt): Resample rate (e.g. "M"). Default is None.
        regrid (str, opt): Regrid resolution. Default is None.
        loglevel (str, opt): Logging level. Default is WARNING.

    Returns:
        data (xarray.DataArray): Reference data.

    Raises:
        NoObservationError: if no reference data is found.
    """
    logger = log_configure(loglevel, 'get_reference_data')

    logger.debug(f"Reference data: {model}-{exp}-{source}")

    try:
        reader = Reader(model=model, exp=exp, source=source, regrid=regrid,
                        loglevel=loglevel)
    except Exception as e:
        raise NoObservationError("Could not retrieve reference data. No plot will be drawn.") from e

    if formula:  # We retrieve all variables
        data = reader.retrieve()
    else:
        data = reader.retrieve(var=varname)

    # Selecting 1991-2020 data as default for the standard deviation
    if formula:
        std = reader.fldmean(eval_formula(varname, data.sel(time=slice("1991", "2020"))).groupby("time.month").std())
    else:
        std = reader.fldmean(data.sel(time=slice("1991", "2020")).groupby("time.month").std())

    if sel:
        logger.debug(f"Selecting {sel}")
        data = data.sel(sel)

    if resample:
        logger.debug(f"Resampling reference data to {resample}")
        data = reader.timmean(data=data, freq=resample)

    if regrid:
        logger.debug(f"Regridding reference data to {regrid}")
        data = reader.regrid(data)

    try:
        if formula:
            return reader.fldmean(eval_formula(varname, data)), std
        else:
            return reader.fldmean(data[varname]), std[varname]
    except KeyError as e:
        logger.error(f"Error: {e}")
        raise NoObservationError(f"Could not retrieve {varname} from reference data. No plot will be drawn.") from e


def plot_timeseries(
    model,
    exp,
    source,
    variable,
    formula=False,
    resample=None,
    regrid=None,
    plot_era5=False,
    ylim={},
    reader_kw={},
    plot_kw={},
    ax=None,
    outfile=None,
    loglevel='WARNING',
    **kwargs,
):
    """
    Plot a time series of the global mean value of a given variable.

    Parameters:
        model (str): Model ID.
        exp (str): Experiment ID.
        source (str): Source ID.
        variable (str): Variable name.
        formula (bool): (Optional) If True, try to derive the variable from other variables.
        resample (str): Optional resample rate (e.g. "M").
        regrid (str): Optional regrid resolution. Default is None.
        plot_era5 (bool): Include ERA5 reference data.
        ylim (dict): Keyword arguments passed to `set_ylim()`.
        reader_kw (dict): Additional keyword arguments passed to the `aqua.Reader`.
        plot_kw (dict): Additional keyword arguments passed to the plotting function.
        ax (matplotlib.Axes): (Optional) axes to plot in.
        outfile (str): (Optional) output file to store data.
        loglevel (str): Logging level. Default is WARNING.

    Raises:
        NotEnoughDataError: if there are not enough data to plot.
        NoDataError: if the variable is not found.
    """

    logger = log_configure(loglevel, 'Plot timeseries')
    if ax is None:
        ax = plt.gca()

    try:
        reader = Reader(model, exp, source, regrid=regrid, **reader_kw, loglevel=loglevel)
    except Exception as e:
        logger.error(f"Error: {e}")
        raise NoDataError(f"Could not retrieve data for {model} {exp} {source}. No plot will be drawn.") from e

    if formula:
        data = reader.retrieve()
        logger.debug(f"Deriving {variable} from other variables")
        try:
            data[variable] = eval_formula(variable, data)
        except KeyError:
            raise KeyError(f'{variable} not possible to evaluate.')
    else:
        try:
            data = reader.retrieve(var=variable)
        except KeyError as e:
            raise NoDataError(f"Could not retrieve {variable} from {model} {exp} {source}. No plot will be drawn.") from e

    data = data[variable]

    if len(data.time) < 2:
        raise NotEnoughDataError("There are not enough data to proceed. Global time series diagnostic requires at least two data points.")

    data = reader.fldmean(data)

    if resample:
        logger.debug(f"Resampling data to {resample}")
        data = reader.timmean(data=data, freq=resample)

    if regrid:
        logger.debug(f"Regridding data to {regrid}")
        data = reader.regrid(data)

    # If no label in plot_kw, use {model}-{exp}
    if "label" not in plot_kw:
        logger.debug(f"Using {model}-{exp} as label")
        plot_kw["label"] = f"{model}-{exp}"

    data.plot(**plot_kw, ax=ax)
    ax.set_title(f'Globally averaged {variable}')

    if outfile is not None:
        logger.debug(f"Saving data to {outfile}")
        data.to_netcdf(outfile)

    if plot_era5:
        eradata, erastd = get_reference_data(
            variable, formula=formula,
            sel={"time": slice(data.time.min(), data.time.max())},
            resample=resample, regrid=regrid,
            loglevel=loglevel
        )
        if eradata is not None:
            eradata.compute()
            erastd.compute()
            ax.fill_between(
                eradata.time,
                eradata - erastd.sel(month=eradata["time.month"]),
                eradata + erastd.sel(month=eradata["time.month"]),
                facecolor="grey",
                alpha=0.3678,
                color="grey",
                label="ERA5",
            )

    ax.legend()
    ax.set_ylim(**ylim)
    ax.grid(axis="x", color="k")
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)


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
    data = reader.timmean(data=data, freq='Y')
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
