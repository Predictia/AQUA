"""Module for scientific utility functions."""
from aqua.logger import log_configure


def area_selection(data=None, lat=None, lon=None, **kwargs):
    """
        Extract a custom area from a DataArray.
        Sets other coordinates to NaN.
        Works on coordinates from 0 to 360, but converts different requests

        Args:
            indat (xarray.DataSet):   input data to be selected
            lat (list, opt):          latitude coordinates
            lon (list, opt):          longitude coordinates

        Keyword Args:
            - box_brd (bool,opt): choose if coordinates are comprised or not.
                                  Default is True
            - loglevel (str, opt): logging level

        Returns:
            (xarray.DataSet):  data on a custom surface

        Raises:
            ValueError: if data is None
            ValueError: if lat and lon are both None
    """
    if data is None:
        raise ValueError('data cannot be None')
    
    # adding safety check since this works only with lon/lat
    if not "lon" in data.coords and not "lat" in data.coords:
        raise KeyError('Cannot find lon and lat in the coordinates, cannot perform area selection')

    lon, lat = check_coordinates(lon=lon, lat=lat, **kwargs)

    box_brd = kwargs.get('box_brd', True)
    # Selection based on box_brd
    if box_brd:
        lat_condition = (data.lat >= lat[0]) & (data.lat <= lat[1])
        # across Greenwich
        if lon[0]>lon[1]:
            lon_condition = ((data.lon >= lon[0]) & (data.lon <= 360)) | ((data.lon >= 0) & (data.lon <= lon[1]))
        else:
            lon_condition = (data.lon >= lon[0]) & (data.lon <= lon[1])
    else:
        lat_condition = (data.lat > lat[0]) & (data.lat < lat[1])
        # across Greenwich
        if lon[0]>lon[1]:
            lon_condition = ((data.lon > lon[0]) & (data.lon < 360)) | ((data.lon > 0) & (data.lon < lon[1]))
        else:
            lon_condition = (data.lon > lon[0]) & (data.lon < lon[1])

    data = data.where(lat_condition & lon_condition)

    return data


def check_coordinates(lon=None, lat=None,
                      default={"lat_min": -90,
                               "lat_max": 90,
                               "lon_min": 0,
                               "lon_max": 360},
                      **kwargs):
    """
        Check if coordinates are valid.
        If not, try to convert them to a valid format.
        Raises an error if coordinates are not valid.

        Args:
            lat (list, opt):          latitude coordinates
            lon (list, opt):          longitude coordinates
            default (dict, opt):      default coordinates system

        Kwargs:
            - loglevel (str, opt): logging level

        Returns:
            (list, list):  latitude and longitude coordinates
    """
    loglevel = kwargs.get('loglevel')
    logger = log_configure(log_level=loglevel, log_name='Check coordinates')

    logger.debug('Input coordinates: lat={}, lon={}'.format(lat, lon))
    logger.debug('Default coordinates: {}'.format(default))

    if lat is None and lon is None:
        raise ValueError('lat and lon cannot be both None')

    if lat:
        lat_min, lat_max = lat
        if lat_min > lat_max:
            # Swap values
            lat = [lat_max, lat_min]
            lat_min, lat_max = lat

        if lat_min < default["lat_min"]:
            raise ValueError('lat_min cannot be lower than {}'.format(default["lat_min"]))
        if lat_max > default["lat_max"]:
            raise ValueError('lat_max cannot be higher than {}'.format(default["lat_max"]))

        lat = [lat_min, lat_max]

    if lon:
        lon_min, lon_max = lon
        # if lon_min > lon_max:
        #     # Swap values
        #     lon = [lon_max, lon_min]
        #     lon_min, lon_max = lon

        logger.debug('lon_min={}, lon_max={}'.format(lon_min, lon_max))

        if default["lon_min"] == 0 and default["lon_max"] == 360:
            logger.debug('Convert to [0,360] range')
            lon_min = _lon_180_to_360(lon_min)
            lon_max = _lon_180_to_360(lon_max)
            logger.debug('lon_min={}, lon_max={}'.format(lon_min, lon_max))
        elif default["lon_min"] == -180 and default["lon_max"] == 180:
            logger.debug('Convert to [-180,180] range')
            lon_min = _lon_360_to_180(lon_min)
            lon_max = _lon_360_to_180(lon_max)
        else:
            raise ValueError('Invalid default coordinates system')

        if lon_min < default["lon_min"]:
            raise ValueError('lon_min cannot be lower than {}'.format(default["lon_min"]))
        if lon_max > default["lon_max"]:
            raise ValueError('lon_max cannot be higher than {}'.format(default["lon_max"]))

        lon = [lon_min, lon_max]

    logger.debug('Output coordinates: lon={}, lat={}'.format(lon, lat))

    return lon, lat


def _lon_180_to_360(lon: float):
    """
    Convert longitude [-180,180] to [0,360] range.
    If lon is already in [0,360] range, it is returned as is.

    Args:
        lon (float): longitude coordinate

    Returns:
        lon (float): converted longitude
    """
    if lon < 0:
        lon = 360 + lon
    return lon


def _lon_360_to_180(lon: float):
    """
    Convert longitude [0,360] to [-180,180] range.
    If lon is already in [-180,180] range, it is returned as is.

    Args:
        lon (float): longitude coordinate

    Returns:
        lon (float): converted longitude
    """
    if lon > 180:
        lon = - 360 + lon
    return lon
