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

class sshVariabilityCompute():
    def __init__(self, data=None, variable=None, catalog=None, model=None, exp=None, source=None, startdate=None, enddate=None, regrid=None, outputdir=None, loglevel='WARNING'):
        """
        Initialize the sshVariability.

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
        self.variable = variable
        self.catalog = catalog
        self.model = model
        self.exp = exp
        self.source = source 
        self.regrid = regrid
        self.startdate = startdate
        self.enddate = enddate
        self.outputdir = outputdir + "/ssh"
        self.logger = log_configure(log_level=loglevel, log_name='SSH Variability Computation')
        self.data = data 

    def save_netcdf(self):
        """
        Save the standard deviation data to a NetCDF file.
        """
        # Create the file type folder within the output directory
        file_type_folder = os.path.join(self.outputdir,"netcdf")
        os.makedirs(file_type_folder, exist_ok=True)

        # Set the output file path
        if self.data is not None:
            output_file = os.path.join(file_type_folder, f"{self.model}_{self.exp}_{self.source}_{self.startdate}_to_{self.enddate}_std.nc")
            self.data.to_netcdf(output_file)
        else:
            self.logger.error("The data can not be saved")

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

