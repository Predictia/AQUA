import pandas as pd
import xarray as xr
from aqua.logger import log_configure
from aqua.diagnostics.core import Diagnostic, convert_data_units
from aqua.util import select_season
from aqua.exceptions import NoDataError
from .util import handle_pressure_level


xr.set_options(keep_attrs=True)


class GlobalBiases(Diagnostic):
    """
    Diagnostic class for computing global and seasonal climatologies of a given variable.

    This class handles data retrieval, pressure level selection, unit conversion, 
    and computation of mean climatologies (total or seasonal).

    Inherits from `Diagnostic`.

    Args:
        catalog (str): The catalog to be used. If None, inferred from Reader.
        model (str): Model to be used.
        exp (str): Experiment name.
        source (str): Source name.
        regrid (str): Target grid for regridding. If None, no regridding.
        startdate (str): Start date for data selection.
        enddate (str): End date for data selection.
        var (str): Variable name to analyze.
        plev (float): Pressure level to select (if applicable).
        save_netcdf (bool): If True, saves output climatologies.
        outputdir (str): Output directory for NetCDF files.
        loglevel (str): Log level. Default is 'WARNING'.
    """
    def __init__(self, catalog=None, model=None, exp=None, source=None,
                 regrid=None, startdate=None, enddate=None,
                 var=None, plev=None,
                 save_netcdf=True, outputdir='./', loglevel='WARNING'):

        super().__init__(catalog=catalog, model=model, exp=exp, source=source,
                         regrid=regrid, startdate=startdate, enddate=enddate,
                         loglevel=loglevel)

        self.logger = log_configure(log_level=loglevel, log_name='Global Biases')
        self.var = var
        self.plev = plev
        self.save_netcdf = save_netcdf
        self.outputdir = outputdir
        self.startdate = startdate
        self.enddate = enddate

    def retrieve(self, var: str = None, plev: float = None, units: str = None) -> None:
        """
        Retrieve and preprocess dataset, selecting pressure level and/or converting units if needed.

        Args:
            var (str, optional): Variable to retrieve. If None, uses self.var.
            plev (float, optional): Pressure level to extract.
            units (str, optional): Target units (e.g., 'mm/day').

        Raises:
            NoDataError: If variable not found in dataset.
            KeyError: If the variable is missing from the data.
        """
        if var is not None:
            self.var = var
        if plev is not None:
            self.plev = plev

        super().retrieve(var=self.var)

        if self.data is None:
            self.logger.error(f"Data could not be retrieved for {self.model}, {self.exp}, {self.source}")
            raise NoDataError("No data retrieved.")

        self.startdate = self.startdate or pd.to_datetime(self.data.time[0].values).strftime('%Y-%m-%d')
        self.enddate = self.enddate or pd.to_datetime(self.data.time[-1].values).strftime('%Y-%m-%d')

        if self.var:
            if self.var not in self.data:
                raise KeyError(f"Variable '{self.var}' not found in dataset variables: {list(self.data.data_vars)}")
            if units:
                self.logger.info(f'Adjusting units for variable {self.var} to {units}.')
                self.data = convert_data_units(self.data, self.var, units, loglevel=self.loglevel)
            if self.plev is not None:
                self.logger.info(f'Selecting pressure level {self.plev} for variable {self.var}.')
                self.data = handle_pressure_level(self.data, self.var, self.plev, loglevel=self.loglevel)
            elif 'plev' in self.data[self.var].dims:
                self.logger.warning(f"Variable {self.var} has multiple pressure levels but none was selected.")
        else:
            self.logger.info("All variables were retrieved. No variable-specific operations applied.")


    def compute_climatology(self,
                            data: xr.Dataset = None,
                            var: str = None,
                            plev: float = None,
                            save_netcdf: bool = None,
                            seasonal: bool = False,
                            seasons_stat: str = 'mean') -> None:
        """
        Compute total and optionally seasonal climatology for a variable.

        Args:
            data (xarray.Dataset, optional): Input dataset. If None, uses self.data.
            var (str, optional): Variable name. If None, uses self.var.
            plev (float, optional): Pressure level (currently unused).
            save_netcdf (bool, optional): If True, save output to NetCDF.
            seasonal (bool): If True, compute seasonal climatology (DJF, MAM, JJA, SON).
            seasons_stat (str): Aggregation statistic: 'mean', 'std', 'max', 'min'.

        Raises:
            ValueError: If `seasons_stat` is invalid.
        """
        data = data or self.data
        var = var or self.var

        if save_netcdf is None:
            save_netcdf = self.save_netcdf

        if data is None:
            raise ValueError("No data provided or retrieved; cannot compute climatology.")

        self.logger.info(f'Computing climatology for variable {var}.')

        self.climatology = xr.Dataset({var: data[var].mean(dim='time')})
        self.climatology.attrs.update({
            'catalog': self.catalog,
            'model': self.model,
            'exp': self.exp,
            'startdate': str(self.startdate),
            'enddate': str(self.enddate)
        })

        if save_netcdf:
            extra_keys = {k: v for k, v in [('var', var), ('plev', plev)] if v is not None}
            super().save_netcdf(
                data=self.climatology,
                diagnostic='globalbiases',
                diagnostic_product='climatology',
                outdir=self.outputdir,
                extra_keys=extra_keys
            )

        if seasonal:
            stat_funcs = {'mean': 'mean', 'max': 'max', 'min': 'min', 'std': 'std'}
            if seasons_stat not in stat_funcs:
                raise ValueError("Invalid statistic. Choose one of 'mean', 'std', 'max', 'min'.")

            self.logger.info(f'Computing seasonal climatology for variable {var}.')

            season_list = ['DJF', 'MAM', 'JJA', 'SON']
            seasonal_data = []

            for season in season_list:
                season_data = select_season(data[var], season)
                season_stat = getattr(season_data, stat_funcs[seasons_stat])(dim='time')
                seasonal_data.append(season_stat.expand_dims(season=[season]))

            self.seasonal_climatology = xr.concat(seasonal_data, dim='season').to_dataset(name=var)
            self.seasonal_climatology.attrs.update({
                'catalog': self.catalog,
                'model': self.model,
                'exp': self.exp,
                'startdate': str(self.startdate),
                'enddate': str(self.enddate)
            })

            if save_netcdf:
                extra_keys = {k: v for k, v in [('var', var), ('plev', plev)] if v is not None}
                super().save_netcdf(
                    data=self.seasonal_climatology,
                    diagnostic='globalbiases',
                    diagnostic_product='seasonal_climatology',
                    outdir=self.outputdir,
                    extra_keys=extra_keys
                )
                self.logger.info(f'Seasonal climatology saved to {self.outputdir}.')
