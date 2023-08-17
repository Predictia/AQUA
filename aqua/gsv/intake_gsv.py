"""An intake driver for FDB/GSV access"""

import sys
import os
import contextlib
import xarray as xr
from intake.source import base
from .timeutil import compute_date_steps, compute_date, check_dates, compute_mars_timerange, compute_steprange, dateobj

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
    version = '0.0.2'
    partition_access = True

    def __init__(self, request, data_start_date, data_end_date, timestyle="date", aggregation="D", timestep="H", startdate=None, enddate=None, var='167', metadata=None, verbose=False, **kwargs):
      """
        Initializes the GSVSource class. These are typically specified in the catalogue entry, but can also be specified upon accessing the catalogue.

        Args:
            request (dict): Request dictionary
            data_start_date (str): Start date of the available data.
            data_end_date (str): End date of the available data.
            timestyle (str, optional): Time style. Defaults to "date".
            aggregation (str, optional): Time aggregation level. Can be one of 10M, 15M, 30M, 1H, H, 3H, 6H, D, 5D, W, M, Y. Defaults to "D". 
            timestep (str, optional): Time step. Can be one of 10M, 15M, 30M, 1H, H, 3H, 6H, D, 5D, W, M, Y. Defaults to "H". 
            startdate (str, optional): Start date for request. Defaults to None.
            enddate (str, optional): End date for request. Defaults to None.
            var (str, optional): Variable ID. Defaults to "167".
            metadata (dict, optional): Metadata read from catalogue. Contains path to FDB.
            verbose (bool, optional): Whether to print additional info to screen. Used only for FDB access. Defaults to False.
            kwargs: other keyword arguments.
    """
        if not startdate:
            startdate = data_start_date
        if not enddate:
            enddate = data_end_date
        
        check_dates(startdate, data_start_date, enddate, data_end_date)

        self.timestyle = timestyle

        if aggregation.upper() == "S":  # special case: 'aggegation at single step level
            aggregation = timestep

        self.aggregation = aggregation
        self.timestep = timestep
        self.data_startdate = data_start_date
        self.data_starttime = "0000"
        self.startdate = startdate
        self.enddate = enddate
        self.starttime = "0000"
        self.endtime = "0000"
        self._var = var
        self.verbose = verbose

        self._request = request
        self._kwargs = kwargs

        self._npartitions = compute_date_steps(startdate, enddate, aggregation,
                                               starttime=self.starttime, endtime=self.endtime)

        if gsv_available:
            self.gsv = GSVRetriever()
        else:
            raise ImportError("FDB5 binary library not present on system or outdated.")
        self._dataset = None
        super(GSVSource, self).__init__(metadata=metadata)

    def _get_schema(self):
        """Standard method providing data schema"""

        return base.Schema(
            datashape=None,
            dtype=xr.Dataset,
            # shape=self._dataset.shape,
            shape=None,
            npartitions=self._npartitions,
            extra_metadata={},
        )

    def _get_partition(self, i):
        """Standard internal method reading i-th data partition from FDB"""

        if self.timestyle == "date":
            dd, tt, _ = compute_date(self.startdate, self.starttime, self.aggregation, i, self._npartitions)
            dform, tform = compute_mars_timerange(dd, tt, self.aggregation, self.timestep)  # computes date and time range in mars style
            self._request["date"] = dform
            self._request["time"] = tform
        else:  # style is 'step'
            self._request["date"] = self.data_startdate
            self._request["time"] = self.data_starttime

            date0 = dateobj(self.data_startdate, self.data_starttime)

            _, _, ndate0 = compute_date(self.startdate, self.starttime, self.aggregation, i, self._npartitions)
            _, _, ndate1 = compute_date(self.startdate, self.starttime, self.aggregation, i + 1, self._npartitions)

            s0 = compute_steprange(date0, ndate0, self.timestep)
            s1 = compute_steprange(date0, ndate1, self.timestep) - 1

            if s0 == s1:
                self._request["step"] = f'{s0}'
            else:
                self._request["step"] = f'{s0}/to/{s1}'

        if self._var:  # if no var provided keep the default in the catalogue
            self._request["param"] = self._var

        if self.verbose:
            print("Request: ", self._request)
            dataset = self.gsv.request_data(self._request)
        else:
            with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
                dataset = self.gsv.request_data(self._request)
        return dataset

    def read(self):
        """Public method providing iterator to read the data"""
        ds = [self._get_partition(i) for i in range(self._npartitions)]
        ds = xr.concat(ds, dim='time')
        return ds

    def to_dask(self):
        return self.read_chunked()

    # def _load(self):
    #     self._dataset = self._get_partition(0)

