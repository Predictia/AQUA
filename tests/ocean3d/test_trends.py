import pytest
from aqua.diagnostics.ocean_trends import Trends



@pytest.mark.diagnostics
def test_trends():
    """Test the trends class."""
    # Create an instance of the trends class
    trend = Trends(catalog='ci', model='FESOM',
                          exp='hpz3', source='monthly-3d',
                          startdate='1990-01-01', enddate='1990-03-31',
                          regrid='r200', loglevel='DEBUG')
    
    trend.run(region='sss')

    assert trend is not None, "trend instance should not be None"