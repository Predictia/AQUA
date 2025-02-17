import pytest 
import xarray as xr
from aqua.diagnostics import SeaIce

# pytest approximation, to bear with different machines
approx_rel = 1e-4
loglevel = 'DEBUG'

@pytest.mark.seaice
class TestSeaIce():
    """Test the SeaIce class."""
    
    @pytest.mark.parametrize(
        ('method', 'region', 'value', 'expected_units'),
        [
            ('extent', 'Arctic', 247.5706, 'million km^2'),
            ('extent', 'Weddell Sea', 56.79711387, 'million km^2'),
            ('volume', 'Arctic', 0.00959179, 'million km^3'), 
            ('volume', 'Antarctic', 0.00749497, 'million km^3')
        ]
    )
    def test_seaice_concentration(self, method, region, value, expected_units):

        seaice = SeaIce(model='ERA5', exp='era5-hpz3', source='monthly', regions=region, 
                        regrid='r100',
                        loglevel=loglevel)
        
        # Only pass threshold if method is 'extent'
        if method == 'extent':
            result = seaice.compute_seaice(method=method, var='tprate', threshold=0)
        elif method == 'volume':
            result = seaice.compute_seaice(method=method, var='tprate')  # No threshold needed for volume
       
        # generate variable name
        regionlower = region.lower().replace(" ", "_")
        var_name = f'sea_ice_{method}_{regionlower}'

        # Assertions
        assert isinstance(result, xr.core.dataset.Dataset)  # Check if result is an xarray dataset
        assert list(result.coords) == ['time']              # Check time dimension
        assert list(result.data_vars) == [var_name]         # Check variable name
        assert result.attrs['units'] == expected_units      # Check units for extent/volume
        assert result[var_name][5].values == pytest.approx(value, rel=approx_rel)
