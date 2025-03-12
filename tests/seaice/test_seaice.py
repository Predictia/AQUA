import pytest 
import xarray as xr
from aqua.diagnostics import SeaIce

# pytest approximation, to bear with different machines
approx_rel = 1e-4
loglevel = 'DEBUG'

@pytest.mark.diagnostics
class TestSeaIce:
    """Test the SeaIce class."""
    
    @pytest.mark.parametrize(
        ('method', 'region', 'value', 'expected_units', 'variable', 'expect_exception', 'error_message'),
        [
            # Valid cases
            ('extent', 'Arctic', 15.3323, 'million km^2', 'siconc', None, None),
            #('extent', 'Weddell Sea', 56.79711387, 'million km^2', 'siconc', None, None),
            #('volume', 'Arctic', 0.00959179, 'thousands km^3', 'siconc', None, None),
            #('volume', 'Antarctic', 0.00749497, 'thousands km^3', 'siconc', None, None),

            # Invalid cases (Errors expected)
            #('wrong_method', 'Antarctic', None, None, 'siconc', ValueError, "Invalid method"),
            #('extent', 'Weddell Sea', None, None, 'errorvar', KeyError, "No variable named ['\"]?errorvar['\"]?"),
            #('volume', 'Antarctic',   None, None, 'errorvar', KeyError, "No variable named ['\"]?errorvar['\"]?")
        ]
    )
    def test_seaice_compute(self, method, region, value, expected_units, 
                            variable, expect_exception, error_message):
        """Test sea ice computation for both valid and invalid cases."""
        
        seaice = SeaIce(model='IFS-NEMO', exp='historical-1990', source='lra-r100-monthly',
                        startdate="1991-01-01", enddate="2000-01-01", regions=region, 
                        regrid='r100', loglevel=loglevel)

        # Handle expected exceptions first
        if expect_exception:
            with pytest.raises(expect_exception, match=error_message):
                if method == 'extent':
                    seaice.compute_seaice(method=method, var=variable, threshold=0.15)  # Only pass threshold kwarg for 'extent'
                else:
                    seaice.compute_seaice(method=method, var=variable)  # No threshold for 'volume'
            return  # Stop further execution for error cases

        # Valid case: compute sea ice
        if method == 'extent':
            result = seaice.compute_seaice(method=method, var=variable, threshold=0.15)  # Only pass threshold kwarg for 'extent'
        else:
            result = seaice.compute_seaice(method=method, var=variable)  #  No threshold for 'volume'

        # Generate variable name dynamically
        regionlower = region.lower().replace(" ", "_")
        var_name = f'sea_ice_{method}_{regionlower}'

        # Assertions for valid results
        assert isinstance(result, xr.Dataset)
        assert list(result.coords) == ['time']
        assert list(result.data_vars) == [var_name]
        assert result.attrs['units'] == expected_units
        assert result[var_name].values[5] == pytest.approx(value, rel=approx_rel)
