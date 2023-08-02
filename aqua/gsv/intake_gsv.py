import sys
import xarray as xr
from intake.source import base

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Test if FDB5 binary library is available
try:
    from gsv.retriever import GSVRetriever
    gsv_available = True
except RuntimeError:
    gsv_available = False


class GSVSource(base.DataSource):
    container = 'xarray'
    name = 'gsv'
    version = '0.0.1'
    partition_access = True

    def __init__(self, request, timestyle="date", aggregation="D", timestep=3600, startdate=None, enddate=None, var='167', metadata=None, **kwargs):
        self.timestyle = timestyle
        self.aggregation = aggregation
        self.timestep = timestep

        self._request = request
        self._kwargs = kwargs
        
        # if startdate and enddate:
        if timestyle == "step":
                self._steps = make_step_range(request, startdate, enddate, timestep)
                self._dates = None
                ndates = len(self._steps)
        else:  # timestyle=="date"
                self._dates = make_date_list(startdate, enddate, aggregation=aggregation)
                self._steps = None
                ndates = len(self._dates)
        #else:
        #    ndates = 1  # read only one
        #    self._dates = None
        #    self._steps = None
        #self._var = var

        self._npartitions = ndates
        if gsv_available:
            self.gsv = GSVRetriever()
        else:
            raise ImportError("FDB5 binary library not present on system or outdated.")
        self._dataset = None
        super(GSVSource, self).__init__(metadata=metadata)

    def _get_schema(self):
        # if self._dataset is None:
        #     self._get_partition(0)
        return base.Schema(
            datashape=None,
            dtype=xr.Dataset,
            # shape=self._dataset.shape,
            shape=None,
            npartitions=self._npartitions,
            extra_metadata={},
        )

    def _get_partition(self, i):
        if self._dates:
            self._request["date"] = self._dates[i]
        elif self._steps:
            self._request["step"] = self._steps[i]
        if self._var:  # if no var provided keep the default in the catalogue
            self._request["param"] = self._var
        dataset = self.gsv.request_data(self._request)
        return dataset

    def read(self):
        ds = [self._get_partition(i) for i in range(self._npartitions)]
        ds = xr.concat(ds, dim='time')
        return ds

    def to_dask(self):
        return self.read_chunked()

    # def _load(self):
    #     self._dataset = self._get_partition(0)


def make_date_list(start, end, aggregation="M"):

    if aggregation == "M":
        delta = relativedelta(months=numsteps)
    elif aggregation == "D":
        delta = relativedelta(days=numsteps)
    elif aggregation == "H":
        delta = relativedelta(hours=numsteps)
    else:
        raise ValueError(f"Aggregation '{aggregation}' not recognized")

    start_date = datetime.strptime(start, '%Y%m%d')
    end_date = datetime.strptime(end, '%Y%m%d')

    date_list = []
    current_date = start_date

    while current_date <= end_date:
        date_string = current_date.strftime('%Y%m%d')
        date_list.append(date_string)
        current_date += delta

    return date_list


def make_step_range(request, start, end, dt):
    """Makes a list of steps between two dates"""

    dt_base = datetime.strptime(f"{request['date']}:{request['time']}", "%Y%m%d:%H%M")
    dt_start = datetime.strptime(f"{start}:0000", "%Y%m%d:%H%M")
    dt_end = datetime.strptime(f"{end}:0000", "%Y%m%d:%H%M")

    step0 = int((dt_start - dt_base).total_seconds() // dt ) 
    step1 = int((dt_end - dt_base).total_seconds() // dt ) 

    return list(range(step0, step1 + 1))


def make_date_list2(start, end, aggregation="M", numsteps=1):

    if step == "M":
        delta = relativedelta(months=numsteps)
    elif step == "D":
        delta = relativedelta(days=numsteps)
    elif step == "H":
        delta = relativedelta(hours=numsteps)
    else:
        sys.exit("step not recognized")

    start_date = datetime.strptime(start, '%Y%m%d')
    end_date = datetime.strptime(end, '%Y%m%d')

    date_list = []
    current_date = start_date

    while current_date <= end_date:
        date_string = current_date.strftime('%Y%m%d')
        date_list.append(date_string)
        current_date += delta

    return date_list


def compute_date(startdate, starttime, step, n):
    # This maps step to timedelta units and format strings
    step_units = {
        '1H': ('hours', 1, '%H%M'),
        '3H': ('hours', 3, '%H%M'),
        '6H': ('hours', 6, '%H%M'),
        'D': ('days', 1, '0000'),
        'W': ('weeks', 1, '0000'),
        'M': ('months', 1, '0000')
        'Y': ('years', 1, '0000')
    }

    # Convert step string to timedelta unit and date format
    step_unit, nsteps, time_format = step_units.get(step.upper())
    if step_unit is None:
        raise ValueError("Invalid step. It should be one of 'H', 'D', or 'M'.")

    # Parse startdate into a datetime object
    start_date_obj = datetime.strptime(startdate + ':' + starttime, '%Y%m%d:%H%M')

    # Calculate the n-th following date
    newdate = start_date_obj + relativedelta(**{step_unit: n * nsteps})

    # Format the date and time
    formatted_date = newdate.strftime('%Y%m%d')
    formatted_time = newdate.strftime(time_format)

    return formatted_date, formatted_time

