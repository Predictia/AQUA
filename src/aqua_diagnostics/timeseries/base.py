import os
from aqua.logger import log_configure
from aqua.util import ConfigPath, load_yaml
from aqua.diagnostics.core import Diagnostic, start_end_dates

class BaseMixin(Diagnostic):
    """Region selection mixin class. Used by """
    def __init__(self, catalog: str = None, model: str = None,
                 exp: str = None, source: str = None,
                 regrid: str = None,
                 startdate: str = None, enddate: str = None,
                 std_startdate: str = None, std_enddate: str = None,
                 region: str = None, lon_limits: list = None, lat_limits: list = None,
                 loglevel: str = 'WARNING'):
        """
        Initialize the Base class.

        Args:
            catalog (str): The catalog to be used. If None, the catalog will be determined by the Reader.
            model (str): The model to be used.
            exp (str): The experiment to be used.
            source (str): The source to be used.
            regrid (str): The target grid to be used for regridding. If None, no regridding will be done.
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
        self.startdate, self.enddate = start_end_dates(startdate=startdate, enddate=enddate,
                                                       start_std=std_startdate, end_std=std_enddate)
        self.std_startdate = self.startdate if std_startdate is None else std_startdate
        self.std_enddate = self.enddate if std_enddate is None else std_enddate

        # Set the region based on the region name or the lon and lat limits
        self._set_region(region=region, lon_limits=lon_limits, lat_limits=lat_limits)

        # Initialize the possible results
        self.hourly = None
        self.daily = None
        self.monthly = None
        self.annual = None
        self.std_hourly = None
        self.std_daily = None
        self.std_monthly = None
        self.std_annual = None

    def _set_region(self, region: str = None, lon_limits: list = None, lat_limits: list = None):
        """
        Set the region to be used.

        Args:
            region (str): The region to select. This will define the lon and lat limits.
            lon_limits (list): The longitude limits to be used. Overridden by region.
            lat_limits (list): The latitude limits to be used. Overridden by region.
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
                    raise ValueError(f'Region {region} not found')
            else:
                self.logger.error('Region file not found')
                raise FileNotFoundError('Region file not found')
        else:
            self.lon_limits = lon_limits
            self.lat_limits = lat_limits
            self.region = None
