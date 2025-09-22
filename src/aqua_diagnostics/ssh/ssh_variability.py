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
        var=None, 
        catalog=None, 
        model=None, 
        exp=None, 
        source=None, 
        startdate=None, 
        enddate=None, 
        regrid=None, 
        outputdir=None, 
        loglevel='WARNING'
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
        super()__init__(catalog=
        self.data = data 
        
        

    def compute(self):
        pass


    def run(self):
        # Retrieve model data and handle potential errors
        try:
            reader = Reader(catalog=self.catalog, model=self.model, exp=self.exp, source=self.source,
                            startdate=self.startdate, enddate=self.enddate, regrid=self.regrid)
            if self.data is not None and self.regrid:
                self.data = reader.regrid(self.data)
            elif self.data is not None and self.regrid is None:
                self.logger.warning(f"Precomputed data for {self.model} may not be reggrid correctly. This could lead to errors in the ssh variabilty calculation")
            else:
                data = reader.retrieve(var=self.variable)
                data = data[self.variable]
                self.data = data.std(axis=0)
                if self.regrid:
                    self.data = reader.regrid(self.data)
                    self.save_netcdf()
                else:
                    self.logger.warning(
                    "No regridding applied. Data is in native grid, "
                    "this could lead to errors in the ssh variability calculation if the data is not in the same grid as the reference data."
                    )

        except Exception as e:
            self.logger.error(f"No model data found: {e}")
            sys.exit("SSH diagnostic terminated.")

        return self.data

