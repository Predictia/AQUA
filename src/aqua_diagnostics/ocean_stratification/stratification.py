import xarray as xr
from aqua.logger import log_configure
from aqua.diagnostics.core import Diagnostic
from aqua.util import to_list
from .util import *

xr.set_options(keep_attrs=True)

class Stratification(Diagnostic):
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
        self.logger = log_configure(log_name="Stratification", log_level=loglevel)

    def run(
        self,
        outputdir: str = ".",
        rebuild: bool = True,
        region: str = None,
        var: list = ["thetao", "so"],
        dim_mean=["lat", "lon"],
        anomaly_ref: str = None,
        reader_kwargs: dict = {},
        mld: bool = False,
        ):
        super().retrieve(var=var, reader_kwargs=reader_kwargs)
        if region:
            super().select_region(region=region, diagnostic="ocean3d")
        if dim_mean:
            self.logger.debug("Averaging data over dimensions: %s", dim_mean)
            self.data = self.data.mean(dim=dim_mean, keep_attrs=True)
        self.stacked_data = self.compute_stratification()
        if mld:
            self.compute_mld()
        # self.save_netcdf(outputdir=outputdir, rebuild=rebuild, region=region)
        self.logger.info("Stratification diagram saved to netCDF file")

    def compute_stratification(self):
        self.compute_climatology(climatology="season")
        self.compute_rho()
        self.logger.debug("Stratification computation completed")
    def compute_climatology(self, climatology: str = "season"):
        """
        Compute climatology for the data.
        
        Args:
            climatology (str): Type of climatology to compute, e.g., 'seasonal'.
        """
        self.logger.debug("Computing %s climatology", climatology)
        self.data = self.data.groupby(f"time.{climatology}").mean("time")
        self.logger.debug("Climatology computed successfully")
    
    def compute_rho(self):
        self.data = convert_variables(self.data, loglevel=self.loglevel)
        # Compute potential density in-situ at reference pressure 0 dbar
        rho = compute_rho(self.data["so"], self.data["thetao"], 0)
        self.data["rho"] = rho -1000  # Convert to kg/m^3
        self.logger.debug("Converted variables to absolute salinity, conservative temperature, and potential density")
    
    def compute_mld(self):
        self.data["mld"] = compute_mld_cont(self.data["rho"], loglevel=self.loglevel)

    def save_netcdf(
        self,
        diagnostic: str = "ocean_drift",
        diagnostic_product: str = "stratification",
        region: str = None,
        outputdir: str = ".",
        rebuild: bool = True,
    ):
        for processed_data in self.processed_data_list:
            super().save_netcdf(
                data=processed_data,
                diagnostic=diagnostic,
                diagnostic_product=f"{diagnostic_product}_{processed_data.attrs['AQUA_ocean_drift_type']}",
                outdir=outputdir,
                rebuild=rebuild,
                extra_keys={"region": region}
            )
            