"""Utilities for calendar and timestep calculations"""

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


step_units = {
    '10M': ('minutes', 10),
    '15M': ('minutes', 15),
    '30M': ('minutes', 30),
    'H': ('hours', 1),
    '1H': ('hours', 1),
    '3H': ('hours', 3),
    '6H': ('hours', 6),
    'D': ('days', 1),
    '1D': ('days', 1),
    '5D': ('days', 5),
    'W': ('days', 7),
    'M': ('months', 1),
    'Y': ('years', 1)
}


def dateobj(startdate, starttime):
    """
    Converts to a date object

    Args:
        startdate (str): Start date in format YYYYMMDD
        starttime (str): Start time in format HHMM

    Returns:
        datetime: Date and time as a datetime object
    """

    return datetime.strptime(str(startdate) + ':' + str(starttime), '%Y%m%d:%H%M')
    

def compute_date(startdate, starttime, step, n, npartitions):
    """
    Computes date at n-th aggegation step

    Args:
        startdate (str): Start date in format YYYYMMDD
        starttime (str): Start time in format HHMM
        step (str): Aggregation step. Can be one of 10M, 15M, 30M, 1H, H, 3H, 6H, D, 5D, W, M, Y
        n (int): Step number
        npartitions (int): Total number of partitions

    Returns:
        formatted_date, formatted_time, newdate
    """
    # compute date at n-th aggregation step

    # Convert step string to timedelta unit and date format
    step_unit, nsteps = step_units.get(step.upper())

    if step_unit in ["days", "months", "years"] and n > 0:  # align at beginning of day for later days
        starttime = "0000"

    # Parse startdate into a datetime object
    tstart = datetime.strptime(str(startdate) + ':' + str(starttime), '%Y%m%d:%H%M')

    # Reset to beginning of month if needed
    if step == "M" and n > 0:
        tstart = tstart.replace(day=1)
    elif step == "Y" and n > 0:
        tstart = tstart.replace(day=1).replace(month=1)

    # Calculate the n-th following date
    newdate = tstart + relativedelta(**{step_unit: n * nsteps})

    # Format the date and time
    formatted_date = newdate.strftime('%Y%m%d')
    formatted_time = newdate.strftime('%H%M')

    return formatted_date, formatted_time, newdate


def compute_date_steps(startdate, enddate, step, starttime="0000", endtime="0000"):
    """
    Compute number of steps between two dates

    Args:
        startdate (str): Start date in format YYYYMMDD
        starttime (str): Start time in format HHMM
        step (str): Aggregation step. Can be one of 10M, 15M, 30M, 1H, H, 3H, 6H, D, 5D, W, M, Y
        starttime (str, optional): Start time in format HHMM. Defaults to "0000".
        endtime (str, optional): End time in format HHMM. Defaults to "0000".

    Returns:
        int: Number of steps
    """

    step_unit, nsteps = step_units.get(step.upper())
    
    startdate = datetime.strptime(str(startdate) + ':' + str(starttime), '%Y%m%d:%H%M')
    enddate = datetime.strptime(str(enddate) + ':' + str(endtime), '%Y%m%d:%H%M')
    
    if step_unit == "months":
        numsteps = (enddate.year - startdate.year) * 12 + enddate.month - startdate.month
    elif step_unit == "years":
        numsteps = enddate.year - startdate.year
    else:
        delta = timedelta(**{step_unit: nsteps})
        numsteps = (enddate - startdate) // delta
    
    return int(numsteps) + 1


def compute_mars_timerange(startdate, starttime, aggregation, timestep):
    """
    Computes date and time ranges in MARS format

    Args:
        startdate (str): Start date in format YYYYMMDD
        starttime (str): Start time in format HHMM
        aggregation (str): Aggregation step. Can be one of 10M, 15M, 30M, 1H, H, 3H, 6H, D, 5D, W, M, Y
        timestep (str): Timestep. Can be one of 10M, 15M, 30M, 1H, H, 3H, 6H, D, 5D, W, M, Y

    Returns:
        dform, tform (str): Date and time range in MARS format
    """

    dform = startdate
    tform = starttime

    if aggregation != timestep:
        # Convert step string to timedelta unit and date format
        ag_unit, ag_nsteps = step_units.get(aggregation.upper())
        ts_unit, ts_nsteps = step_units.get(timestep.upper())

        ts = relativedelta(**{ts_unit: ts_nsteps})
        agg = relativedelta(**{ag_unit: ag_nsteps})

        tstart = datetime.strptime(str(startdate) + ':' + str(starttime), '%Y%m%d:%H%M')

        if (((tstart + agg) - (tstart + ts) ).total_seconds()) < 0:
            raise ValueError(f"Aggregation {aggregation} is shorter than timestep {timestep}!")

        if ag_unit == "minutes" or ag_unit == "hours":
            # Aggregation smaller than one day
            tstart = datetime.strptime(str(startdate) + ':' + str(starttime), '%Y%m%d:%H%M') 
            tend = tstart + agg - ts
            tform = tstart.strftime('%H%M') + '/to/' + tend.strftime('%H%M') + '/by/' + f"{ts.hours:02d}{ts.minutes:02d}"
        else:
            if ts_unit == "minutes" or ts_unit == "hours":
                # Timestep is shorter than one day
                tend = datetime.strptime(str(startdate) + ':0000', '%Y%m%d:%H%M') + relativedelta(days=1) - ts
                tform = '0000/to/' + tend.strftime('%H%M') + '/by/' + f"{ts.hours:02d}{ts.minutes:02d}"
            else:
                tform = starttime

            if ((tstart + agg) - tstart).days > 1:  # more than one day
                tstart0 = tstart
                # If month or year reset to beginning of period
                if aggregation == "M":
                    tstart0 = datetime.strptime(tstart.strftime('%Y%m01:0000'), '%Y%m%d:%H%M')
                elif aggregation == "Y":
                    tstart0 = datetime.strptime(tstart.strftime('%Y0101:0000'), '%Y%m%d:%H%M')

                tend = tstart0 + agg - relativedelta(days=1)
                dform = tstart.strftime('%Y%m%d') + '/to/' + tend.strftime('%Y%m%d')

    return dform, tform


def compute_steprange(startdate_obj, newdate_obj, timestep):
    """
    Compute number of steps between two dates

    Args:
        startdate_obj (datetime.datetime): Start date
        newdate_obj (datetime.datetime): End date
        timestep (str): Timestep. Can be one of 10M, 15M, 30M, 1H, H, 3H, 6H, D, 5D, W, M, Y

    Returns:
        int: Number of steps
    """

    ts_unit, ts_nsteps = step_units.get(timestep.upper())

    if ts_unit == "months":
        delta = relativedelta(newdate_obj, startdate_obj)
        return delta.years * 12 + delta.months
    elif ts_unit == "years":
        delta = relativedelta(newdate_obj, startdate_obj)
        return delta.years
    else:
        ts = timedelta(**{ts_unit: ts_nsteps})
        return (newdate_obj - startdate_obj) // ts


def check_dates(startdate, start_date, enddate, end_date):
    """
    Check if starting and ending dates are within given range

    Args:
        startdate (datetime.datetime): Starting date
        start_date (datetime.datetime): Data start date
        enddate (datetime.datetime): Ending date
        end_date (datetime.datetime): Data end date

    Raises:
        ValueError: If the given date is not within the data range
    """

    if datetime.strptime(str(startdate), '%Y%m%d') < datetime.strptime(str(start_date), '%Y%m%d'):
        raise ValueError(f"Starting date {str(startdate)} is earlier than the data start at {str(start_date)}.")

    if datetime.strptime(str(enddate), '%Y%m%d') > datetime.strptime(str(end_date), '%Y%m%d'):
        raise ValueError(f"End date {str(enddate)} is later than the data end at {str(end_date)}.")
    

def set_stepmin(startdate, starttime, stepmin, step):
    """
    Make sure that we start at the earliest available date
    Args:
        startdate (str): Starting date
        starttime (str): Starting time
        stepmin (int): Earliest step
        step (str): Timestep. Can be one of 10M, 15M, 30M, 1H, H, 3H, 6H, D, 5D, W, M, Y
    Returns:
        A revised startdate and starttime (str)
    """

    ts_unit, ts_nsteps = step_units.get(timestep.upper())
    ts = timedelta(**{ts_unit: ts_nsteps * stepmin})
    
    newdate = dateobj(startdate, starttime) + ts
    return datetime.strptime(str(newdate), '%Y%m%d'), datetime.strptime(str(newdate), '%H%M')


def set_stepmin(tgtdate, tgttime, startdate, starttime, stepmin, step):
    """
    Make sure that we start at the earliest available date
    Args:
        tgtdate (str): Desired date
        tgttime (str): Desired time
        startdate (str): Data starting date
        starttime (str): Data starting time
        stepmin (int): Earliest step
        step (str): Timestep. Can be one of 10M, 15M, 30M, 1H, H, 3H, 6H, D, 5D, W, M, Y
    Returns:
        A revised date and time (str)
    """

    ts_unit, ts_nsteps = step_units.get(step.upper())
    ts = timedelta(**{ts_unit: ts_nsteps * stepmin})
    
    date0 = dateobj(startdate, starttime) + ts
    date1 = dateobj(tgtdate, tgttime)
    newdate = max(date0, date1)
    
    return datetime.strftime(newdate, '%Y%m%d'), datetime.strftime(newdate, '%H%M')