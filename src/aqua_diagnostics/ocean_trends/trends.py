import xarray as xr
from aqua.logger import log_configure
from aqua.diagnostics.core import Diagnostic
from aqua.util import area_selection
from itertools import product
from aqua import reader
from aqua.reader import Trender


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
        region, lon_limits, lat_limits = super().select_region(diagnostic="ocean3d", region=region)
        
        if dim_mean:
            self.data = self.data.mean(dim=dim_mean, keep_attrs=True)
        self.trend_coef = self.compute_trend(data = self.data, loglevel=self.loglevel)
        self.save_netcdf(outputdir= outputdir, rebuild=rebuild, region=region)
    
    def adjust_trend_for_time_frequency(self, trend, y_array, loglevel= "WARNING"):
        """
        Adjust the trend values based on time frequency.

        Parameters:
            trend (dask.array): Trend values.
            y_array (xarray.DataArray): Input array containing the variable of interest.
            loglevel (str, optional): Log level for logging messages. Defaults to "WARNING".

        Returns:
            dask.array: Trend values adjusted for time frequency.
        """
        time_frequency = y_array["time"].to_index().inferred_freq
        
        if time_frequency == None:
            time_index = pd.to_datetime(y_array["time"].values)
            time_diffs = time_index[1:] - time_index[:-1]
            is_monthly = all(time_diff.days >= 28 for time_diff in time_diffs)
            if is_monthly == True:
                time_frequency= "MS"
            else:
                raise ValueError(f"The frequency of the data must be in Daily/Monthly/Yearly")
                
            
        if time_frequency == "MS":
            trend = trend * 12
        elif time_frequency == "H":
            trend = trend * 24 * 30 * 12
        elif time_frequency == "Y" or 'YE-DEC':
            trend = trend
        else:
            raise ValueError(f"The frequency: {time_frequency} of the data must be in Daily/Monthly/Yearly")
        
        trend.attrs['units'] = f"{trend.attrs['units']}/year"
        return trend
    
    def compute_trend(self, data, loglevel= "WARNING"):
        """
        Compute the trend values for temperature and salinity variables in a 3D dataset.

        Parameters:
            data (xarray.Dataset): Input dataset containing temperature (thetao) and salinity (so) variables.
            loglevel (str, optional): Log level for logging messages. Defaults to "WARNING".

        Returns:
            xarray.Dataset: Dataset with trend values for temperature and salinity variables.
        """
        logger = log_configure(loglevel, 'TS_3dtrend')
        logger.debug("Calculating linear trend")

        trend_init = Trender()
        trend_data = trend_init.coeffs(data, dim= 'time',skipna= True, normalize= True)
        trend_data.attrs = data.attrs
        trend_dict = {}
        for var in data.data_vars:
            trend_dict[var] = self.adjust_trend_for_time_frequency(trend_data[var], data, loglevel=loglevel)
            trend_dict[var].attrs = data[var].attrs
        
        logger.debug("Trend value calculated")
        return trend_data
    
    
    def save_netcdf(self, diagnostic: str = "trends",
                    diagnostic_product: str = "spatial_trend",
                    region: str = None,
                    outputdir: str = '.', rebuild: bool = True):
    
        save_kwargs = {}

        # if region is not None:
        #     save_kwargs["region"] = region
        
        super().save_netcdf(
            diagnostic=diagnostic,
            diagnostic_product=diagnostic_product,
            outdir=outputdir,
            rebuild=rebuild,
            data=self.trend_coef,
            extra_keys={"region": region.replace(" ", "_") if region else None},
        )