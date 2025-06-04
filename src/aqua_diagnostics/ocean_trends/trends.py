import xarray as xr
from aqua.logger import log_configure
from aqua.diagnostics.core import Diagnostic
from aqua.util import area_selection
from itertools import product

xr.set_options(keep_attrs=True)

class Trends(Diagnostic):
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
        super().__init__(catalog=catalog, model=model,
                         exp=exp, source=source, regrid=regrid,
                         startdate=startdate, enddate=enddate,
                         loglevel=loglevel)
        self.logger = log_configure(log_name="Trends", log_level=loglevel)
    
    def run(self, outputdir: str = ".", rebuild: bool = True,
            region: str = None, var: list = ["thetao", "so"], dim_mean: type = None):
        super().retrieve(var=var)
        region, lon_limits, lat_limits = super()._set_region(diagnostic="ocean3d", region=region)
        
        if dim_mean:
            self.data = self.data.mean(dim=dim_mean, keep_attrs=True)
        self.save_netcdf(outputdir=outputdir, rebuild=rebuild, region=region)

    
    def compute_trend(self):
        print(self.data)
    
    def save_netcdf(self, diagnostic: str = "ocean_drift",
                    diagnostic_product: str = "hovmoller",
                    region: str = None,
                    outputdir: str = '.', rebuild: bool = True):
    
        save_kwargs = {}

        if region is not None:
            save_kwargs["region"] = region
        