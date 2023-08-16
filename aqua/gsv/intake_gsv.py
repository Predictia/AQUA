import sys
import xarray as xr
from intake.source import base
from .timeutil import compute_date, compute_steps, check_dates, compute_mars_timerange

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

    def __init__(self, request, start_date, end_date, timestyle="date", aggregation="D", timestep="H", startdate=None, enddate=None, var='167', metadata=None, **kwargs):

        if not startdate:
            startdate = start_date
        if not enddate:
            enddate = end_date
        
        check_dates(startdate, start_date, enddate, end_date)

        self.timestyle = timestyle
        if aggregation.upper() == "S":  # special case: 'aggegation at single step level
            aggregation = timestep
        self.aggregation = aggregation
        self.timestep = timestep
        self.startdate = startdate
        self.enddate = enddate
        self.starttime = "0000"
        self.endtime = "0000"
        self._var = var

        self._request = request
        self._kwargs = kwargs
        
        # print("timestyle", timestyle, " aggregation", aggregation, "timestep", timestep)
        # if startdate and enddate:
        if timestyle == "step":
                self._steps = make_step_range(request, startdate, enddate, timestep)
                self._dates = None
                ndates = len(self._steps)
        else:  # timestyle=="date"
                ndates = compute_steps(startdate, enddate, aggregation, starttime="0000", endtime="0000")

        #         self._dates = make_date_list(startdate, enddate, aggregation=aggregation)
        #         self._steps = None
        #         ndates = len(self._dates)

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
        # if self._dates:
        #     self._request["date"] = self._dates[i]
        # elif self._steps:
        #     self._request["step"] = self._steps[i]

        if self.timestyle == "date":
            dd, tt = compute_date(self.startdate, self.starttime, self.aggregation, i)
            dform, tform = compute_mars_timerange(dd, tt, self.aggregation, self.timestep)  # computes date and time range in mars style
            self._request["date"] = dform
            self._request["time"] = tform
        if self._var:  # if no var provided keep the default in the catalogue
            self._request["param"] = self._var
        print(self._request)
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


