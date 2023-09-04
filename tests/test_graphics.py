import pytest
import xarray as xr
import numpy as np

from aqua.util.graphics import add_cyclic_lon

@pytest.fixture()
def da():
    """Create a test DataArray"""
    lon_values = np.linspace(0, 360, 36)  # Longitude values
    lat_values = np.linspace(-90, 90, 18)  # Latitude values
    data = np.random.rand(18, 36)  # Example data
    return xr.DataArray(data, dims=['lat', 'lon'], coords={'lon': lon_values, 'lat': lat_values})


@pytest.mark.graphics
def test_add_cyclic_lon(da):
    old_da = da.copy()
    new_da = add_cyclic_lon(da)

    # Assertions to test the function
    assert isinstance(new_da, xr.DataArray), "Output should be an xarray.DataArray"
    assert 'lon' in new_da.coords, "Output should have a 'lon' coordinate"
    assert 'lat' in new_da.coords, "Output should have a 'lat' coordinate"
    assert np.allclose(new_da.lat, old_da.lat), "Latitude values should be equal"
    assert np.allclose(new_da.isel(lon=-1).values, old_da.isel(lon=0).values), "First and last longitude values should be equal"
    assert new_da.shape == (18, 37), "Output shape is incorrect"
