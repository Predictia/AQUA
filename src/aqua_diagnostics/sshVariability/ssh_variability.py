import os
import gc
import sys
import numpy as np
import pandas as pd
import xarray as xr
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from aqua import Reader
from aqua.exceptions import NotEnoughDataError, NoDataError, NoObservationError
from aqua.util import create_folder, coord_names, area_selection
from aqua import Reader, plot_single_map
from aqua.logger import log_configure

class sshVariabilityCompute(BaseMixin):
    """
    SSH Computation
    """
    def __init__(
        self,
        diagnostic_name: str = "sshVariability",
        catalog: str = None,
        model: str = None,
        exp: str = None,
        source: str = None,
        startdate: str = None,
        enddate: str = None,
        region: str = None,
        regrid: str = None,
        lon_limits: list[float] = None,
        lat_limits: list[float] = None,
        zoom: float = None,
        outputdir: str = "./",
        reader_kwargs: dict = {}
        var: str = None,
        long_name: str = None,
        short_name: str = None,
        units: str = None,
        save_netcdf: bool = True,
        rebuild: bool = True,
        loglevel: str = "WARNING",
    ):
 
        """
        Initialize the 'sshVariabilityCompute' class.

        This class is designed to load an xarray.Dataset and computes std. It can load either load data using the Reader class or takes in input xarray.Dataset and regrids it using the Reader.regrid method. It then returns the xarray.Dataset. 
        Args:
            variable (str): Variable name
            catalog (str): catalog 
            data: xarray.Dataset 
            model (str): Name of the data
            exp (str): Name of the experiment
            source (str): the source
            startdate (str): Start date 
            enddate  (str): End date 
            regrid (str): Regrid option for regridding
            outputdir (str): output directory
            loglevel (str): Default WARNING
        """
        super()__init__(catalog=catalog, model=model, exp=exp, source=source, startdate=startdate, enddate=enddate, region=region, regrid=regrid, lon_limits=lon_limits, lat_limits=lat_limits, zoom=zoom, reader_kwargs=reader_kwargs, var=var, long_name=long_name, short_name=short_name, units=untis, outputdir=outputdir, rebuild=rebuild, loglevel=loglevel)
        
        self.save_netcdf = save_netcdf
        self.data_std = None 

    def run(self):
        # Retrieve model data, compute STD and handle potential errors.
        super().retrieve(var=var, reader_kwargs=reader_kwargs)
        if self.data is None:
            raise ValueError(f'Variable {self.var} not found in the data. '
                                'Check the variable name and the data source.')
        try:
            self.data_std = self.data[self.var].std(dim="time")
            if self.save_netcdf:
                self.logger.info(f"Output std netcdf file is saved at {self.outputdir}.")
                self.netcdf_save(data=self.data_std)
            else:
                self.logger.info("Output in netcdf is not saved.")
        except Exception as e:
            self.logger.error(f"No model data found: {e}")
            sys.exit("SSH diagnostic terminated.")


