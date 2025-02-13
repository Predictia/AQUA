import pytest 
import xarray as xr
from aqua.diagnostics import SeaIce

def test_seaice_concentration():

    seaice = SeaIce(model='ERA5', exp='era5-hpz3', source='monthly', regions=['Arctic'], regrid='r100')
    extent = seaice.compute_seaice(method='extent', var='tprate', threshold=0)

    assert isinstance(extent, xr.Dataset)
    assert list(extent.coords) == ['time']
    assert list(extent.data_vars) == ['sea_ice_extent_arctic']
    assert extent.attrs['units'] == 'million km^2'
    assert pytest.approx(extent['sea_ice_extent_arctic'][5].values) == 247.5706