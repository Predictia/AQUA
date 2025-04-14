import pandas as pd
import xarray as xr
from aqua.logger import log_configure
from aqua.diagnostics.core import Diagnostic
from aqua.util import area_selection
from .util import data_process_by_type, predefined_regions
from itertools import product

xr.set_options(keep_attrs=True)

class Hovmoller(Diagnostic):
    """
    Hovmoller class for generating Hovmoller diagrams from ocean model data.
    This class inherits from the Diagnostic class and provides methods to retrieve,
    process, and save the netcdf for Hovmoller diagrams.
    """
    def __init__(self, catalog=None, model = None, exp = None, source = None,
                regrid = None, startdate = None, enddate = None,
                loglevel='WARNING'):
        """
        Initialize the Hovmoller class.

        Parameters
        ----------
        config : dict
            Configuration dictionary containing the parameters for the Hovmoller diagram.
        """
        super().__init__(catalog=catalog, model=model, exp=exp, source=source,
                        regrid=regrid, startdate=startdate, enddate=enddate,
                        loglevel=loglevel)
        self.logger = log_configure(log_name='Hovmoller', log_level=loglevel)
    
    def run(self, outputdir = None, region = None,  var = ['thetao', 'so']):
        self.outputdir = outputdir
        self.region = region
        self.var = var
        self.logger.info("Running Hovmoller diagram generation")
        self.retrieve()
        self.area_select()
        self.process_data(dim_mean = ["lat","lon"])
        self.save_netcdf(diagnostic = "Hovmoller", diagnostic_product = "Hovmoller")
        self.logger.info("Hovmoller diagram saved to netcdf file")
    
    def retrieve(self):
        self.data, self.reader, self.catalog = super()._retrieve(catalog=self.catalog, model=self.model,
                                                        exp=self.exp, source=self.source, var=self.var,
                                                        regrid=self.regrid, startdate=self.startdate,
                                                        enddate=self.enddate)
    def area_select(self):
        if self.region is not None:
            lat_s, lat_n, lon_w, lon_e = predefined_regions(self.region)
            self.data = area_selection(data = self.data, lat = [lat_n, lat_s], lon = [lon_w, lon_e], drop = True)
    
    def process_data(self, dim_mean : None):

        
        if dim_mean is not None:
            self.data = self.data.mean(dim=dim_mean)
        data_list = []

        for anomaly, standardise, anomaly_ref in product([False, True], [False, True], ["t0", "tmean"]):
            data_proc, type, cmap = data_process_by_type(
                data = self.data,
                anomaly = anomaly,
                standardise = standardise,
                anomaly_ref = anomaly_ref,
                loglevel = self.loglevel,
            )

            data_proc.attrs["cmap"] = cmap
            data_proc = data_proc.expand_dims(dim={"type": [type]})
            
            data_list.append(data_proc)
        
        self.stacked_data = xr.concat(data_list, dim="type")
                    
    def save_netcdf(self, diagnostic, diagnostic_product, rebuild = True):
        super().save_netcdf(data=self.stacked_data, diagnostic=diagnostic,
                            diagnostic_product = diagnostic_product, outputdir = self.outputdir, rebuild = rebuild)
        