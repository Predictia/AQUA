'''
This module contains miscellaneous tools for the teleconnections diagnostic.
- loading functions, to deal with yaml files
'''
import xarray as xr


def check_dim(data, dim: str):
    """
    Check if dimension is in data.

    Args:
        data:   DataArray
        dim (str):          Dimension

    Raises:
        ValueError:         If dimension is not in data
    """
    if isinstance(data, xr.Dataset):
        data = data[list(data.keys())[0]]

    if dim not in data.dims:
        raise ValueError(f'{dim} not in {data.dims}')
