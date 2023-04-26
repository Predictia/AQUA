
"""The module contains functions useful for xarrays:
     - xarray_attribute_update,
     - data_size

.. moduleauthor:: AQUA team <natalia.nazarova@polito.it>

"""

def xarray_attribute_update(xr1, xr2):
    """Combining the attributes of two xarrays

    Args:
        xr1 (xarray): xarray, to which we would like to add attributes
        xr2 (xarray): xarray, which attributes we want to pass to another xarray

    Returns:
        xarray: xarray with combained attributes
    """
    combined_attrs = {**xr1.attrs, **xr2.attrs}
    history_attr  = xr1.attrs['history'] +  xr2.attrs['history']
    xr1.attrs = combined_attrs
    xr1.attrs['history'] = history_attr
    return xr1


def data_size(data):
    """Returning the size of the Dataset or DataArray

    Args:
        data (xarray): Dataset or dataArray, the size of which we would like to return
    Returns:
        int: size of data
    """ 
    if 'DataArray' in str(type(data)):
            size = data.size
    elif 'Dataset' in str(type(data)): 
        names = list(data.dims) #_coord_names)
        size = 1
        for i in names:
            size *= data[i].size
    return size
