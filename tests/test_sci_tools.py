import pytest

import xarray as xr
import numpy as np
from aqua.util import area_selection

@pytest.fixture
def sample_data():
    # Create a sample DataArray for testing
    data = xr.DataArray(
        np.random.rand(6,6),
        coords={'lat': [10, 20, 30, 40, 50, 60], 'lon': [40, 50, 60, 70, 80, 90]},
        dims=['lat', 'lon']
    )
    return data

def test_valid_selection(sample_data):
    # Test with valid latitude and longitude ranges
    lat_range = [15, 25]
    lon_range = [45, 55]
    result = area_selection(sample_data, lat=lat_range, lon=lon_range, box_brd=True)

    assert result is not None
    assert np.isnan(result.sel(lat=10))
    #assert result.lon.values.tolist() == [50]

def test_invalid_lat_lon(sample_data):
    # Test with invalid latitude and longitude ranges
    lat_range = [25, 15]  # Invalid, should raise a ValueError
    lon_range = [55, 45]  # Invalid, should raise a ValueError

    with pytest.raises(ValueError):
        area_selection(sample_data, lat=lat_range, lon=lon_range, box_brd=True)

def test_missing_lat_lon(sample_data):
    # Test when both lat and lon are None, should raise a ValueError
    with pytest.raises(ValueError):
        area_selection(sample_data, lat=None, lon=None, box_brd=True)

def test_invalid_lat_order(sample_data):
    # Test with lat in descending order, should raise a ValueError
    lat_range = [25, 15]

    with pytest.raises(ValueError):
        area_selection(sample_data, lat=lat_range, lon=[45, 55], box_brd=True)

def test_invalid_lon_order(sample_data):
    # Test with lon in descending order, should raise a ValueError
    lon_range = [55, 45]

    with pytest.raises(ValueError):
        area_selection(sample_data, lat=[15, 25], lon=lon_range, box_brd=True)

def test_missing_lat_lon_coords(sample_data):
    # Test with missing lat or lon coordinates, should raise an AttributeError
    data_missing_lat = xr.DataArray(np.random.rand(3, 3), coords={'lon': [40, 50, 60]}, dims=['lat', 'lon'])
    data_missing_lon = xr.DataArray(np.random.rand(3, 3), coords={'lat': [10, 20, 30]}, dims=['lat', 'lon'])

    with pytest.raises(AttributeError):
        area_selection(data_missing_lat, lat=[15, 25], lon=[45, 55], box_brd=True)

    with pytest.raises(AttributeError):
        area_selection(data_missing_lon, lat=[15, 25], lon=[45, 55], box_brd=True)
