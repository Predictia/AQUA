"""Utility for the GlobalBiases module"""

import xarray as xr
from aqua.exceptions import NoDataError

def fix_precipitation_units(data, var):
    """
    Converts precipitation units from kg m-2 s-1 to mm/day.

    Args:
        data (xr.Dataset): Dataset to adjust.
        var (str): Variable name for precipitation.

    Returns:
        xr.Dataset: Dataset with adjusted units.
    """
    if data[var].attrs['units'] != 'mm/day':
        data[var] *= 86400
        data[var].attrs['units'] = 'mm/day'
    return data


def select_pressure_level(data, plev, var):
    """
    Selects a specified pressure level from the dataset if necessary.

    Args:
        data (xr.Dataset): Dataset to select from.
        plev (float): Desired pressure level.
        var (str): Variable name to filter by.

    Returns:
        xr.Dataset: Filtered dataset at the specified pressure level.
    """
    if var not in data:
        raise NoDataError(f"Variable '{var}' not found in the dataset.")

    # Check if 'plev' is a dimension
    if 'plev' in data[var].dims:
        # If 'plev' is already in coordinates and matches the selected level, return as is
        if 'plev' in data[var].coords and data[var].coords['plev'].size == 1:
            if data[var].coords['plev'].values[0] == plev:
                return data  # Already at the requested level
        # Otherwise, try selecting the specified pressure level
        try:
            return data.sel(plev=plev)
        except KeyError:
            raise NoDataError(f"The specified pressure level {plev} is not in the dataset.")
    else:
        raise NoDataError(f"Variable '{var}' does not have a 'plev' dimension.")

