import os

import xarray as xr
from aqua.exceptions import NoDataError
from aqua.logger import log_configure
from aqua.util import ConfigPath
from aqua.util import convert_units, eval_formula, load_yaml, frequency_string_to_pandas
from aqua.diagnostics.core import Diagnostic, start_end_dates

from .util import loop_seasonalcycle

xr.set_options(keep_attrs=True)


class Timeseries(Diagnostic):
    """Timeseries class for retrieve and netcdf saving of a single experiment"""

    def __init__(self, catalog: str = None, model: str = None,
                 exp: str = None, source: str = None,
                 regrid: str = None, std: bool = False,
                 startdate: str = None, enddate: str = None,
                 std_startdate: str = None, std_enddate: str = None,
                 region: str = None, lon_limits: list = None, lat_limits: list = None,
                 loglevel: str = 'WARNING'):
        """
        Initialize the Timeseries class.

        Args:
            catalog (str): The catalog to be used. If None, the catalog will be determined by the Reader.
            model (str): The model to be used.
            exp (str): The experiment to be used.
            source (str): The source to be used.
            regrid (str): The target grid to be used for regridding. If None, no regridding will be done.
            std (bool): If True, a ribbon for standard deviation will be computed. Default is False.
            startdate (str): The start date of the data to be retrieved.
                             If None, all available data will be retrieved.
            enddate (str): The end date of the data to be retrieved.
                           If None, all available data will be retrieved.
            std_startdate (str): The start date of the standard period. Ignored if std is False.
            std_enddate (str): The end date of the standard period. Ignored if std is False.
            region (str): The region to select. This will define the lon and lat limits.
            lon_limits (list): The longitude limits to be used. Overriden by region.
            lat_limits (list): The latitude limits to be used. Overriden by region.
            loglevel (str): The log level to be used. Default is 'WARNING'.
        """
        super().__init__(catalog=catalog, model=model, exp=exp, source=source, regrid=regrid,
                         loglevel=loglevel)

        self.logger = log_configure(log_level=loglevel, log_name='TimeSeries')

        # We want to make sure we retrieve the required amount of data with a single Reader instance
        # However, if no standard deviation, we can ignore std_startdate and std_enddate
        std_startdate = std_startdate if std else None
        std_enddate = std_enddate if std else None
        self.startdate, self.enddate = start_end_dates(startdate=startdate, enddate=enddate,
                                                       start_std=std_startdate, end_std=std_enddate)

        # Set the region based on the region name or the lon and lat limits
        self._set_region(region=region, lon_limits=lon_limits, lat_limits=lat_limits)

        # Initialize the possible results
        self.hourly = None
        self.daily = None
        self.monthly = None
        self.annual = None
        self.std = std
        if self.std:
            self.std_hourly = None
            self.std_daily = None
            self.std_monthly = None
            self.std_annual = None

    def retrieve(self, var: str, formula: bool = False, long_name: str = None,
                 units: str = None, standard_name: str = None):
        """
        Retrieve the data for the given variable.

        Args:
            var (str): The variable to be retrieved.
            formula (bool): If True, the variable is a formula.
            long_name (str): The long name of the variable, if different from the variable name.
            units (str): The units of the variable, if different from the original units.
            standard_name (str): The standard name of the variable, if different from the variable name.
        """
        # If the user requires a formula the evaluation requires the retrieval
        # of all the variables
        if formula:
            super().retrieve()
            self.logger.debug("Evaluating formula %s", var)
            self.data = eval_formula(mystring=var, xdataset=self.data)
            if self.data is None:
                self.logger.error('Error evaluating formula %s', var)
                raise NoDataError('Error evaluating formula %s' % var)
        else:
            super().retrieve(var=var)
            if self.data is None:
                self.logger.error('Error retrieving variable %s', var)
                raise NoDataError('Error retrieving variable %s' % var)
            # Get the xr.DataArray to be aligned with the formula code
            self.data = self.data[var]

        # Customization of the data, expecially needed for formula
        if units is not None:
            self._check_data(var, units)
        if long_name is not None:
            self.data.attrs['long_name'] = long_name
        if standard_name is not None:
            self.data.attrs['standard_name'] = standard_name
            self.data.name = standard_name

    def compute(self, freq: str, exclude_incomplete: bool = True,
                center_time: bool = True, box_brd: bool = True):
        """
        Compute the mean of the data. Support for hourly, daily, monthly and annual means.

        Args:
            freq (str): The frequency to be used for the resampling.
            exclude_incomplete (bool): If True, exclude incomplete periods.
            center_time (bool): If True, the time will be centered.
            box_brd (bool,opt): choose if coordinates are comprised or not in area selection.
                                Default is True
        """
        if freq is None:
            self.logger.error('Frequency not provided')
            raise ValueError('Frequency not provided')

        freq = frequency_string_to_pandas(freq)
        str_freq = self._str_freq(freq)

        # Field and time average
        data = self.reader.fldmean(self.data, box_brd=box_brd,
                                   lon_limits=self.lon_limits, lat_limits=self.lat_limits)
        data = self.reader.timmean(data, freq=freq, exclude_incomplete=exclude_incomplete,
                                   center_time=center_time)

        if str_freq == 'hourly':
            self.hourly = data
        elif str_freq == 'daily':
            self.daily = data
        elif str_freq == 'monthly':
            self.monthly = data
        elif str_freq == 'annual':
            self.annual = data
    
    def compute_std(self, freq: str, exclude_incomplete: bool = True, center_time: bool = True,
                    box_brd: bool = True):
        """
        Compute the standard deviation of the data. Support for monthly and annual frequencies.

        Args:
            freq (str): The frequency to be used for the resampling.
            exclude_incomplete (bool): If True, exclude incomplete periods.
            center_time (bool): If True, the time will be centered.
            box_brd (bool,opt): choose if coordinates are comprised or not in area selection.
                                Default is True
        """
        if freq is None:
            self.logger.error('Frequency not provided')
            raise ValueError('Frequency not provided')

        freq = frequency_string_to_pandas(freq)
        str_freq = self._str_freq(freq)
        
        std_stardate = self.startdate if self.std_startdate is None else self.std_startdate
        std_enddate = self.enddate if self.std_enddate is None else self.std_enddate

        data = self.data.isel(time=slice(std_stardate, std_enddate))
        data = self.reader.fldmean(data, box_brd=box_brd,
                                   lon_limits=self.lon_limits, lat_limits=self.lat_limits)

        data = self.reader.timstd(data, freq=freq, exclude_incomplete=exclude_incomplete,
                                  center_time=center_time)
        
        if str_freq == 'hourly':
            self.std_hourly = data
        elif str_freq == 'daily':
            self.std_daily = data
        elif str_freq == 'monthly':
            self.std_monthly = data
        elif str_freq == 'annual':
            self.std_annual = data

    def save_netcdf(self, freq: str, outputdir: str = './', rebuild: bool = True,
                    **kwargs):
        """
        Save the data to a netcdf file.
        
        Args:
            freq (str): The frequency of the data.
            outputdir (str): The directory to save the data.
            rebuild (bool): If True, rebuild the data from the original files.

        Keyword Args:
            **kwargs: Additional keyword arguments to be passed to the OutputSaver.save_netcdf method.
        """
        if freq is None:
            self.logger.error('Frequency not provided')
            raise ValueError('Frequency not provided')
        else:
            str_freq = self._str_freq(freq)

        if str_freq == 'hourly':
            data = self.hourly if self.hourly is not None else self.logger.error('No hourly data available')
            data_std = self.std_hourly if self.std_hourly is not None else None
        elif str_freq == 'daily':
            data = self.daily if self.daily is not None else self.logger.error('No daily data available')
            data_std = self.std_daily if self.std_daily is not None else None
        elif str_freq == 'monthly':
            data = self.monthly if self.monthly is not None else self.logger.error('No monthly data available')
            data_std = self.std_monthly if self.std_monthly is not None else None
        elif str_freq == 'annual':
            data = self.annual if self.annual is not None else self.logger.error('No annual data available')
            data_std = self.std_annual if self.std_annual is not None else None

        diagnostic_product = data.name
        super().save_netcdf(data=data, diagnostic='timeseries', diagnostic_product=diagnostic_product,
                            default_path=outputdir, rebuild=rebuild, **kwargs)
        if self.std:
            diagnostic_product = f'{diagnostic_product}_std'
            super().save_netcdf(data=data_std, diagnostic='timeseries', diagnostic_product=diagnostic_product,
                                default_path=outputdir, rebuild=rebuild, **kwargs)

    def _set_region(self, region: str = None, lon_limits: list = None, lat_limits: list = None):
        """
        Set the region to be used.

        Args:
            region (str): The region to select. This will define the lon and lat limits.
            lon_limits (list): The longitude limits to be used. Overriden by region.
            lat_limits (list): The latitude limits to be used. Overriden by region.
        """
        if region is not None:
            region_file = ConfigPath().get_config_dir()
            region_file = os.path.join(region_file, 'diagnostics',
                                       'timeseries', 'interface', 'regions.yaml')
            if os.path.exists(region_file):
                regions = load_yaml(region_file)
                if region in regions['regions']:
                    self.lon_limits = regions['regions'][region].get('lon_limits', None)
                    self.lat_limits = regions['regions'][region].get('lat_limits', None)
                    self.region = regions['regions'][region].get('logname', region)
                    self.logger.info(f'Region {self.region} found, using lon: {self.lon_limits}, lat: {self.lat_limits}')
                else:
                    self.logger.error('Region %s not found', region)
                    raise ValueError('Region %s not found' % region)
            else:
                self.logger.error('Region file not found')
                raise FileNotFoundError('Region file not found')
        else:
            self.lon_limits = lon_limits
            self.lat_limits = lat_limits
            self.region = None
    
    def _check_data(self, var: str, units: str):
        """
        Make sure that the data is in the correct units.

        Args:
            var (str): The variable to be checked.
            units (str): The units to be checked.
        """
        final_units = units
        initial_units = self.data.units
        data = self.data

        conversion = convert_units(initial_units, final_units)

        factor = conversion.get('factor', 1)
        offset = conversion.get('offset', 0)

        if factor != 1 or offset != 0:
            self.logger.debug('Converting %s from %s to %s',
                              var, initial_units, final_units)
            data = data * factor + offset
            data.attrs['units'] = final_units
            self.data = data

    def _str_freq(self, freq: str):
        """
        Args:
            freq (str): The frequency to be used.
        
        Returns:
            str_freq (str): The frequency as a string.
        """
        if freq in ['h', 'hourly']:
            str_freq = 'hourly'
        elif freq in ['D', 'daily']:
            str_freq = 'daily'
        elif freq in ['MS', 'ME', 'M', 'mon', 'monthly']:
            str_freq = 'monthly'
        elif freq in ['YS', 'YE', 'Y', 'annual']:
            str_freq = 'annual'
        else:
            self.logger.error('Frequency %s not recognized', freq)
            raise ValueError('Frequency %s not recognized' % freq)
        
        return str_freq
