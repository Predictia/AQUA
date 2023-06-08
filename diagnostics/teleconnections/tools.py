'''
This module contains simple tools for the teleconnections diagnostic.
- loading functions, to deal with yaml files
'''
from aqua.util import load_yaml, get_config_dir


def area_selection(indat, lat=None, lon=None, box_brd=True):
    """
        Extract a custom area from a DataArray.

        Args:
            indat (DataArray):      input data to be selected
            lat (list, opt):        latitude coordinates
            lon (list, opt):        longitude coordinates
            box_brd (bool,opt):     choose if coordinates are
                                    comprised or not.
                                    Default is True

        Returns:
            odat (DataArray):       data on a custom surface
    """
    # 1. -- Extract coordinates from indat --
    if lat is None and lon is None:
        raise ValueError('lat and lon cannot be both None')
    if lat:
        if lat[0] > lat[1]:
            raise ValueError('lat must be specified in ascending order')
        else:
            lat_coord = indat.lat
    if lon:
        if lon[0] > lon[1]:
            raise ValueError('lon must be specified in ascending order')
        else:
            lon_coord = indat.lon

    # 2. -- Select area --
    if box_brd:
        if lat:
            iplat = lat_coord.where((lat_coord >= lat[0]) &
                                    (lat_coord <= lat[1]), drop=True)
        if lon:
            iplon = lon_coord.where((lon_coord >= lon[0]) &
                                    (lon_coord <= lon[1]), drop=True)
    else:
        if lat:
            iplat = lat_coord.where((lat_coord > lat[0]) &
                                    (lat_coord < lat[1]), drop=True)
        if lon:
            iplon = lon_coord.where((lon_coord > lon[0]) &
                                    (lon_coord < lon[1]), drop=True)

    # 3. -- Are selection --
    odat = indat
    if lat:
        odat = odat.sel(lat=iplat)
    if lon:
        odat = odat.sel(lon=iplon)

    return odat


def load_namelist(diagname='teleconnections', configdir=None):
    """
    Load diagnostic yaml file.

    Args:
        diagname (str, opt):    diagnostic name. Default is 'teleconnections'
        configdir (str, opt):   path to config directory. Default is Nones

    Returns:
        namelist (dict):        Diagnostic configuration
    """
    if configdir is None:
        filename = f'{diagname}.yaml'
        configdir = get_config_dir(filename)

    infile = f'{configdir}/{diagname}.yaml'
    namelist = load_yaml(infile)

    return namelist
