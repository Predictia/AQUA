import xarray as xr
from aqua.logger import log_configure
from aqua.diagnostics.core import Diagnostic
from aqua.util import to_list

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
        ):
        super().retrieve(var=var, reader_kwargs=reader_kwargs)
        super().select_region(region=region, diagnostic="ocean3d")
        self.stacked_data = self.compute_stratification()
        self.save_netcdf(outputdir=outputdir, rebuild=rebuild, region=region)
        self.logger.info("Stratification diagram saved to netCDF file")

    def compute_stratification(self):
        self.compute_climatology()
        self.compute_rho()
        if self.mld:  
            self.compute_mld()
        
    def compute_climatology(self):
    
    def compute_rho(self):
    
    def compute_mld(self):
        
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
            