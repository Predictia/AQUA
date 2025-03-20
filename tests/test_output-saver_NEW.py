import pytest
import xarray as xr
import matplotlib.pyplot as plt
from aqua.logger import log_configure
from aqua.util import OutputSaver_NEW, open_image

# Initialize the logger for the tests
log_configure(log_level='DEBUG', log_name='OutputSaverTest')


# Fixture for OutputSaver instance
@pytest.fixture
def output_saver():
    return OutputSaver_NEW(diagnostic='dummy', model='MSWEP', exp='past',
                       catalog='lumi-phase2', loglevel='DEBUG')

@pytest.mark.aqua
def test_generate_name(output_saver):
    """Test the generation of output filenames with and without additional parameters."""
    # Test filename generation without additional parameters
    filename = output_saver.generate_name(diagnostic_product='mean', var='tprate')
    assert filename == 'dummy.mean.lumi-phase2.MSWEP.past.tprate'

    # Test filename generation with extra keys
    extra_keys = {
        'catalog_2': 'lumi-phase3', 'model_2': 'ERA5', 'exp_2': 'era5', 'region': 'indian_ocean'
    }
    filename = output_saver.generate_name(diagnostic_product='mean', var='tprate', extra_keys=extra_keys)
    assert filename == 'dummy.mean.lumi-phase2.MSWEP.past.tprate.lumi-phase3.ERA5.era5.indian_ocean' 

