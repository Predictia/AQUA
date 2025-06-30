"""Module for scientific utility functions."""
import xarray as xr
from aqua.logger import log_configure, log_history

# set default options for xarray
xr.set_options(keep_attrs=True)


def area_selection(data=None, lat=None, lon=None,
                   box_brd=True, drop=False,
                   **kwargs):
    """
        Extract a custom area from a DataArray.
        Sets other coordinates to NaN.
        Works on coordinates from 0 to 360, but converts different requests

        Args:
            indat (xarray.DataSet):   input data to be selected
            lat (list, opt):          latitude coordinates
            lon (list, opt):          longitude coordinates
            box_brd (bool,opt):       choose if coordinates are comprised or not.
                                      Default is True
            drop (bool, opt):         drop coordinates not in the selected area.
                                      Default is False

        Keyword Args:
            - loglevel (str, opt): logging level (default: 'warning')

        Returns:
            (xarray.DataSet):  data on a custom surface

        Raises:
            ValueError: if data is None
            KeyError:   if 'lon' or 'lat' are not in the coordinates
            ValueError: if lat and lon are both None
    """
    
    if data is None:
        raise ValueError('data cannot be None')

    # adding safety check since this works only with lon/lat
    if "lon" not in data.coords or "lat" not in data.coords:
        raise KeyError('Cannot find lon and lat in the coordinates, cannot perform area selection')

    if lat is None and lon is None:
        raise ValueError('lat and lon cannot be both None')

    lon, lat = check_coordinates(lon=lon, lat=lat, **kwargs)

    # Selection based on box_brd
    if box_brd:
        lat_condition = (data.lat >= lat[0]) & (data.lat <= lat[1])
        # across Greenwich
        if lon[0] > lon[1]:
            lon_condition = (
                (data.lon >= lon[0]) & (data.lon <= 360)
            ) | (
                (data.lon >= 0) & (data.lon <= lon[1])
            )
        else:
            lon_condition = (data.lon >= lon[0]) & (data.lon <= lon[1])
    else:
        lat_condition = (data.lat > lat[0]) & (data.lat < lat[1])
        # across Greenwich
        if lon[0] > lon[1]:
            lon_condition = (
                (data.lon > lon[0]) & (data.lon < 360)
            ) | (
                (data.lon > 0) & (data.lon < lon[1])
            )
        else:
            lon_condition = (data.lon > lon[0]) & (data.lon < lon[1])

    data = data.where(lat_condition & lon_condition, drop=drop)

    data = log_history(data, f"Area selection: lat={lat}, lon={lon}")

    return data


def check_coordinates(lon=None, lat=None,
                      default={"lat_min": -90,
                               "lat_max": 90,
                               "lon_min": 0,
                               "lon_max": 360},
                      loglevel='WARNING'):
    """
        Check if coordinates are valid.
        If not, try to convert them to a valid format.
        Raises an error if coordinates are not valid.

        Args:
            lat (list, opt):          latitude coordinates
            lon (list, opt):          longitude coordinates
            default (dict, opt):      default coordinates system
            loglevel (str, opt):      logging level. Default is 'WARNING'.

        Returns:
            (list, list):  latitude and longitude coordinates
    """
    logger = log_configure(log_level=loglevel, log_name='Check coordinates')

    logger.debug('Input coordinates: lat=%s, lon=%s', lon, lat)
    logger.debug('Default coordinates: %s', default)

    if lat is None and lon is None:
        raise ValueError('lat and lon cannot be both None')

    if lat:
        lat_min, lat_max = lat

        if lat_min is None and lat_max is None:
            logger.info('lat_min and lat_max are None, setting them to default values')
            lat_min = default["lat_min"]
            lat_max = default["lat_max"]

        if lat_min > lat_max:
            # Swap values
            lat = [lat_max, lat_min]
            lat_min, lat_max = lat

        if lat_min < default["lat_min"]:
            raise ValueError(f'lat_min cannot be lower than {default["lat_min"]}')
        if lat_max > default["lat_max"]:
            raise ValueError(f'lat_max cannot be higher than {default["lat_max"]}')

        lat = [lat_min, lat_max]

    if lon:
        lon_min, lon_max = lon

        if lon_min is None and lon_max is None:
            logger.info('lon_min and lon_max are None, setting them to default values')
            lon_min = default["lon_min"]
            lon_max = default["lon_max"]
        # if lon_min > lon_max:
        #     # Swap values
        #     lon = [lon_max, lon_min]
        #     lon_min, lon_max = lon

        logger.debug('lon_min=%s, lon_max=%s', lon_min, lon_max)

        if lon_min == 0 and lon_max == 360:
            logger.debug('Convert manually since conversion will give the same values twice')
            lon_min = default["lon_min"]
            lon_max = default["lon_max"]
        else:
            if default["lon_min"] == 0 and default["lon_max"] == 360:
                logger.debug('Convert to [0,360] range')
                lon_min = _lon_180_to_360(lon_min)
                lon_max = _lon_180_to_360(lon_max)
                logger.debug('lon_min=%s, lon_max=%s', lon_min, lon_max)
            elif default["lon_min"] == -180 and default["lon_max"] == 180:
                logger.debug('Convert to [-180,180] range')
                lon_min = _lon_360_to_180(lon_min)
                lon_max = _lon_360_to_180(lon_max)
            else:
                raise ValueError('Invalid default coordinates system')

            if lon_min < default["lon_min"]:
                raise ValueError(f'lon_min cannot be lower than {default["lon_min"]}')
            if lon_max > default["lon_max"]:
                raise ValueError(f'lon_max cannot be higher than {default["lon_max"]}')

        lon = [lon_min, lon_max]

    # If lat or lon are None, set them to default values
    if lat is None:
        lat = [default["lat_min"], default["lat_max"]]
    if lon is None:
        lon = [default["lon_min"], default["lon_max"]]

    # If lat min and max are the same, set them to default values
    # same for lon
    if lat[0] == lat[1]:
        lat = [default["lat_min"], default["lat_max"]]
        logger.warning('lat_min and lat_max are the same, setting them to default values')
    if lon[0] == lon[1]:
        lon = [default["lon_min"], default["lon_max"]]
        logger.warning('lon_min and lon_max are the same, setting them to default values')

    logger.debug('Output coordinates: lat=%s, lon=%s', lat, lon)

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

def select_season(xr_data, season: str):
    """
    Select a season from a xarray.DataArray or xarray.Dataset.
    Available seasons are:
    - DJF: December-January-February
    - JFM: January-February-March
    - FMA: February-March-April
    - MAM: March-April-May
    - AMJ: April-May-June
    - MJJ: May-June-July
    - JJA: June-July-August
    - JAS: July-August-September
    - ASO: August-September-October
    - SON: September-October-November
    - OND: October-November-December
    - NDJ: November-December-January
    Args:
        xr_data (xarray.DataArray or xarray.Dataset): input data
        season (str):                                 season to be selected
    Returns:
        (xarray.DataArray or xarray.Dataset): selected season
    """
    triplet_months = {
        'DJF': [12, 1, 2],
        'JFM': [1, 2, 3],
        'FMA': [2, 3, 4],
        'MAM': [3, 4, 5],
        'AMJ': [4, 5, 6],
        'MJJ': [5, 6, 7],
        'JJA': [6, 7, 8],
        'JAS': [7, 8, 9],
        'ASO': [8, 9, 10],
        'SON': [9, 10, 11],
        'OND': [10, 11, 12],
        'NDJ': [11, 12, 1]
    }

    if season in triplet_months:
        selected_months = triplet_months[season]
        selected =  xr_data.sel(time=(xr_data['time.month'] == selected_months[0]) | (xr_data['time.month'] == selected_months[1]) | (xr_data['time.month'] == selected_months[2]))
        # Add AQUA_season attribute
        selected.attrs['AQUA_season'] = season
        return selected
    elif season == 'annual':
        return xr_data
    else:
        raise ValueError(f"Invalid season abbreviation. Available options are: {', '.join(triplet_months.keys())}, or 'annual' to perform no season selection.")
