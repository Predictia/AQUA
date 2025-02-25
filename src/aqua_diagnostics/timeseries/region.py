import os
from aqua.util import ConfigPath, load_yaml

class RegionMixin:
    """Region selection mixin class. Used by """
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
