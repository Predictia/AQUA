import pytest 
import xarray as xr
from aqua.diagnostics import SeaIce

# pytest approximation, to bear with different machines
approx_rel = 1e-4
loglevel = 'DEBUG'

@pytest.mark.seaice
class TestSeaIce():
    """Test the SeaIce class."""

    @pytest.mark.parametrize(('region,value'), 
                             [('Arctic', 247.5706),
                              ('Weddell Sea', 56.79711387)
                              ])
    def test_seaice_concentration(self, region, value):

        seaice = SeaIce(model='ERA5', exp='era5-hpz3', source='monthly', regions=region, regrid='r100',
                        loglevel=loglevel)
        extent = seaice.compute_seaice(method='extent', var='tprate', threshold=0)
        regionlower = region.lower().replace(" ", "_")