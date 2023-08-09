"""Utilities for calendar and timestep calculations"""

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


step_units = {
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

def compute_date(startdate, starttime, step, n):
    # This maps step to timedelta units and format strings

    # Convert step string to timedelta unit and date format
    step_unit, nsteps = step_units.get(step.upper())

    # Parse startdate into a datetime object
    start_date_obj = datetime.strptime(str(startdate) + ':' + str(starttime), '%Y%m%d:%H%M')

    # Calculate the n-th following date
    newdate = start_date_obj + relativedelta(**{step_unit: n * nsteps})

    # Format the date and time
    formatted_date = newdate.strftime('%Y%m%d')
    formatted_time = newdate.strftime('%H%M')

    return formatted_date, formatted_time


def compute_steps(startdate, enddate, step, starttime="0000", endtime="0000"):
    """Compute number of steps between two dates"""

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


def compute_enddate(startdate, starttime, step):
    # This maps step to timedelta units and format strings

    # Convert step string to timedelta unit and date format
    step_unit, nsteps = step_units.get(step.upper())

    # Parse startdate into a datetime object
    start_date_obj = datetime.strptime(str(startdate) + ':' + str(starttime), '%Y%m%d:%H%M')

    # Calculate the n-th following date
    newdate = start_date_obj + relativedelta(**{step_unit: n * nsteps})

    # Format the date and time
    formatted_date = newdate.strftime('%Y%m%d')
    formatted_time = newdate.strftime('%H%M')

    return formatted_date, formatted_time

def check_dates(startdate, start_date, enddate, end_date):
    if datetime.strptime(str(startdate), '%Y%m%d') < datetime.strptime(str(start_date), '%Y%m%d'):
        raise ValueError(f"Starting date {str(startdate)} is earlier than the data start at {str(start_date)}.")

    if datetime.strptime(str(enddate), '%Y%m%d') > datetime.strptime(str(end_date), '%Y%m%d'):
        raise ValueError(f"End date {str(enddate)} is later than the data end at {str(end_date)}.")