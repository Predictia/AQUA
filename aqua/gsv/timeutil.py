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


def compute_date(startdate, starttime, step, n):
    # This maps step to timedelta units and format strings

    # Convert step string to timedelta unit and date format
    step_unit, nsteps = step_units.get(step.upper())

    # Parse startdate into a datetime object
    tstart = datetime.strptime(str(startdate) + ':' + str(starttime), '%Y%m%d:%H%M')

    if n > 0:
        # Reset to beginning of month if needed
        if step == "M":
            tstart = datetime.strptime(tstart.strftime('%Y%m01:0000'), '%Y%m%d:%H%M')
        elif step == "Y":
            tstart = datetime.strptime(tstart.strftime('%Y0101:0000'), '%Y%m%d:%H%M')

    # Calculate the n-th following date
    newdate = tstart + relativedelta(**{step_unit: n * nsteps})

    # Format the date and time
    formatted_date = newdate.strftime('%Y%m%d')
    formatted_time = newdate.strftime('%H%M')

    return formatted_date, formatted_time


def compute_date_steps(startdate, enddate, step, starttime="0000", endtime="0000"):
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


def compute_mars_timerange(startdate, starttime, aggregation, timestep):
    # This computes time ranges in mars format

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


def compute_mars_steprange(startdate, starttime, aggregation, timestep):
    # This computes number of ste

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


def check_dates(startdate, start_date, enddate, end_date):
    if datetime.strptime(str(startdate), '%Y%m%d') < datetime.strptime(str(start_date), '%Y%m%d'):
        raise ValueError(f"Starting date {str(startdate)} is earlier than the data start at {str(start_date)}.")

    if datetime.strptime(str(enddate), '%Y%m%d') > datetime.strptime(str(end_date), '%Y%m%d'):
        raise ValueError(f"End date {str(enddate)} is later than the data end at {str(end_date)}.")