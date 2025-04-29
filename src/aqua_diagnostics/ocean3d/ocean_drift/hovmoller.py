import pandas as pd
import xarray as xr
from aqua.logger import log_configure
from aqua.diagnostics.core import Diagnostic
from aqua.util import area_selection
from .util import predefined_regions, _data_process_for_drift

xr.set_options(keep_attrs=True)


class Hovmoller(Diagnostic):
    """
    A class for generating Hovmoller diagrams from ocean model data.

    This class provides methods to retrieve, process, and save netCDF files
    for Hovmoller diagrams. It inherits from the `Diagnostic` class.

    Attributes:
        logger (Logger): Logger instance for the class.
        outputdir (str): Directory to save the output files.
        region (str): Region for area selection.
        var (list): List of variables to process.
        stacked_data (xarray.Dataset): Processed data for Hovmoller diagrams.
    """

    def __init__(
        self,
        catalog: str = None,
        model: str = None,
        exp: str = None,
        source: str = None,
        regrid: str = None,
        startdate: str = None,
        enddate: str = None,
        loglevel: str = "WARNING",
    ):
        """
        Initializes the Hovmoller class.

        Args:
            catalog (str, optional): Path to the catalog file.
            model (str, optional): Model name.
            exp (str, optional): Experiment name.
            source (str, optional): Data source.
            regrid (str, optional): Regridding method.
            startdate (str, optional): Start date for data retrieval.
            enddate (str, optional): End date for data retrieval.
            loglevel (str, optional): Logging level. Defaults to "WARNING".
        """
        super().__init__(
            catalog=catalog,
            model=model,
            exp=exp,
            source=source,
            regrid=regrid,
            startdate=startdate,
            enddate=enddate,
            loglevel=loglevel,
        )
        self.logger = log_configure(log_name="Hovmoller", log_level=loglevel)

    def run(self, outputdir: str = None, region: str = None, var: list = None):
        if var is None:
            var = ["thetao", "so"]
        """
        Executes the Hovmoller diagram generation process.

        Args:
            outputdir (str, optional): Directory to save the output files.
            region (str, optional): Region for area selection.
            var (list, optional): List of variables to process. Defaults to ["thetao", "so"].
        """
        self.outputdir = outputdir
        self.region = region
        self.var = var
        self.logger.info("Running Hovmoller diagram generation")
        super().retrieve(var = var)
        self.logger.info("Data retrieved successfully")
        self.area_select()
        self.stacked_data = _data_process_for_drift(
            data=self.data, dim_mean=["lat", "lon"]
        )
        self.save_netcdf(diagnostic="Hovmoller", diagnostic_product="Hovmoller")
        self.logger.info("Hovmoller diagram saved to netCDF file")

    def area_select(self):
        """
        Applies area selection to the retrieved data.

        If a region is specified, the data is filtered based on the
        predefined region's latitude and longitude bounds.
        """
        if self.region is not None:
            lon_limits, lat_limits = predefined_regions(self.region)
            self.data = area_selection(
                data=self.data, lat=lat_limits, lon=lon_limits, drop=True
            )
        else:
            self.logger.warning("Since region name is not specified, processing whole region in the dataset")
            
            
    def save_netcdf(self, diagnostic, diagnostic_product, rebuild=True):
        """
        Saves the processed data to a netCDF file.

        Args:
            diagnostic (str): Name of the diagnostic.
            diagnostic_product (str): Name of the diagnostic product.
            rebuild (bool, optional): Whether to rebuild the netCDF file. Defaults to True.
        """
        super().save_netcdf(
            data=self.stacked_data,
            diagnostic=diagnostic,
            diagnostic_product=diagnostic_product,
            outputdir=self.outputdir,
            rebuild=rebuild,
        )
