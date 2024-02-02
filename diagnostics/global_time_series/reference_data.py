"""
Functions to retrieve reference data for global time series diagnostics.
"""
from aqua import Reader
from aqua.logger import log_configure
from aqua.exceptions import NoObservationError


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
        loglevel (str): Logging level. Default is WARNING.

    Returns:
        dict: dictionary with 2m temperature and net radiation at TOA for reference data.
              A center value is given together with the standard deviation for the selected period.
    """
    logger = log_configure(loglevel, 'get_reference_gregory')

    if startdate is not None or enddate is not None:
        logger.info(f"Reference data will be retrieved rom {startdate} to {enddate}.")
    else:
        logger.info("Reference data will be retrieved for the full period.")
    logger.info(f"Retrieving reference data for {ts_name} from {ts_ref['model']} {ts_ref['exp']} {ts_ref['source']}.")
    logger.info(f"Retrieving reference data for {toa_name} from {toa_ref['model']} {toa_ref['exp']} {toa_ref['source']}.")

    # Retrieve and evaluate ts:
    try:
        reader_ts = Reader(ts_ref['model'], ts_ref['exp'], ts_ref['source'],
                           startdate=startdate, enddate=enddate, loglevel=loglevel)

        data_ts = reader_ts.retrieve(var=ts_name)
        data_ts = data_ts[ts_name]
        data_ts = reader_ts.timmean(data_ts, freq='YS')
        data_ts = reader_ts.fldmean(data_ts)

        logger.debug("Evaluating 2m temperature")

        ts_std = data_ts.std().values
        ts_mean = data_ts.mean().values

        logger.debug(f"Mean: {ts_mean}, Std: {ts_std}")
    except Exception as e:
        logger.debug(f"Error: {e}")
        logger.error(f"Failed to retrieve {ts_name} from {ts_ref['model']} {ts_ref['exp']}.")
        ts_std = None
        ts_mean = None

    # Retrieve and evaluate toa:
    try:
        reader_toa = Reader(toa_ref['model'], toa_ref['exp'], toa_ref['source'],
                            startdate=startdate, enddate=enddate, loglevel=loglevel)
        data_toa = reader_toa.retrieve(var=toa_name)
        data_toa = data_toa[toa_name[0]] + data_toa[toa_name[1]]
        data_toa = reader_toa.timmean(data_toa, freq='YS')
        data_toa = reader_toa.fldmean(data_toa)

        logger.debug("Evaluating net radiation at TOA")

        toa_std = data_toa.std().values
        toa_mean = data_toa.mean().values

        logger.debug(f"Mean: {toa_mean}, Std: {toa_std}")
    except Exception as e:
        logger.debug(f"Error: {e}")
        logger.error(f"Failed to retrieve {toa_name} from {toa_ref['model']} {toa_ref['exp']}.")
        toa_std = None
        toa_mean = None

    if ts_std is None and toa_std is None:
        raise NoObservationError("No reference data available. No plot will be drawn.")

    return {'ts': {'mean': ts_mean, 'std': ts_std},
            'toa': {'mean': toa_mean, 'std': toa_std}}
