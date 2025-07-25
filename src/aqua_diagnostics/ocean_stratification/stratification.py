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
        dim_mean= None,
        reader_kwargs: dict = {},
        mld: bool = False,
        ):
        self.logger.info("Starting stratification diagnostic run.")
        super().retrieve(var=var, reader_kwargs=reader_kwargs)
        self.logger.debug(f"Variables retrieved: {var}, region: {region}, dim_mean: {dim_mean}")
        if region:
            self.logger.info(f"Selecting region: {region} for diagnostic 'ocean3d'.")
            super().select_region(region=region, diagnostic="ocean3d")
        if dim_mean:
            self.logger.debug(f"Averaging data over dimensions: {dim_mean}")
            self.data = self.data.mean(dim=dim_mean, keep_attrs=True)
        self.logger.info("Computing stratification.")
        self.compute_stratification()
        if mld:
            self.logger.info("Computing mixed layer depth (MLD).")
            self.compute_mld()
        self.save_netcdf(outputdir=outputdir, rebuild=rebuild, region=region)
        self.logger.info("Stratification diagnostic saved to netCDF file.")

    def compute_stratification(self):
        self.logger.debug("Starting computation of climatology and density.")
        self.compute_climatology(climatology="season")
        self.compute_rho()
        self.logger.debug("Stratification computation completed successfully.")
    def compute_climatology(self, climatology: str = "season"):
        """
        Compute climatology for the data.
        
        Args:
            climatology (str): Type of climatology to compute, e.g., 'seasonal'.
        """
        self.logger.debug(f"Computing {climatology} climatology.")
        self.data = self.data.groupby(f"time.{climatology}").mean("time")
        self.logger.debug(f"{climatology.capitalize()} climatology computed successfully.")
    
    def compute_rho(self):
        self.logger.debug("Converting variables to absolute salinity and conservative temperature.")
        self.data = convert_variables(self.data, loglevel=self.loglevel)
        self.logger.debug("Computing potential density at reference pressure 0 dbar.")
        rho = compute_rho(self.data["so"], self.data["thetao"], 0)
        self.data["rho"] = rho - 1000  # Convert to kg/m^3
        self.logger.debug("Added 'rho' (potential density anomaly) to dataset.")
    
    def compute_mld(self):
        self.logger.debug("Computing mixed layer depth (MLD) from density.")
        mld = compute_mld_cont(self.data[["rho"]], loglevel=self.loglevel)
        self.data["mld"] = mld["mld"]
        self.logger.debug("Added 'mld' (mixed layer depth) to dataset.")

    def save_netcdf(
        self,
        diagnostic: str = "ocean_drift",
        diagnostic_product: str = "stratification",
        region: str = None,
        outputdir: str = ".",
        rebuild: bool = True,
    ):
        self.logger.info(f"Saving results to netCDF: diagnostic={diagnostic}, product={diagnostic_product}, outputdir={outputdir}, region={region}")
        super().save_netcdf(
            data=self.data,
            diagnostic=diagnostic,
            diagnostic_product=f"{diagnostic_product}",
            outdir=outputdir,
            rebuild=rebuild,
            extra_keys={"region": region}
        )
        self.logger.info("NetCDF file saved successfully.")
            