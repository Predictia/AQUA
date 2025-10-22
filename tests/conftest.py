"""
Shared fixtures for AQUA test suite.
These fixtures use scope="session" to retrieve data once and share across all tests.
Reference: https://docs.pytest.org/en/stable/reference/fixtures.html
"""
import pytest
from aqua import Reader

LOGLEVEL = "DEBUG"

# =============================================================================
# Fixtures for custom configurations
# =============================================================================
@pytest.fixture
def custom_reader():
    """
    Fixture to create readers with custom kwargs.
    Use this when you need special configurations like rebuild=True, 
    different regrid options, or other kwargs that aren't covered by 
    the standard session fixtures.
    
    Example usage in tests:
        def test_something(custom_reader):
            reader = custom_reader(model='IFS', exp='test-tco79', source='short',
                                    regrid='r100', rebuild=True )
            data = reader.retrieve(var='2t')
            # ... test code
    """
    def _create_custom_reader(model=None, exp=None, source=None, catalog='ci', 
                              loglevel=LOGLEVEL, **kwargs):
        """Create a Reader instance with custom configuration"""
        return Reader(catalog=catalog, model=model, exp=exp,
                      source=source, loglevel=loglevel, **kwargs)
    return _create_custom_reader

# =============================================================================
# IFS fixtures
# =============================================================================
@pytest.fixture(scope="session")
def ifs_tco79_short_reader():
    return Reader(model="IFS", exp="test-tco79", source="short", loglevel=LOGLEVEL)

@pytest.fixture(scope="session")
def ifs_tco79_short_data(ifs_tco79_short_reader):
    return ifs_tco79_short_reader.retrieve()

@pytest.fixture(scope="session")
def ifs_tco79_short_data_2t(ifs_tco79_short_reader):
    return ifs_tco79_short_reader.retrieve(var='2t')

@pytest.fixture(scope="session")
def ifs_tco79_short_r100_reader():
    return Reader(model="IFS", exp="test-tco79", source="short", loglevel=LOGLEVEL, regrid="r100")

@pytest.fixture(scope="session")
def ifs_tco79_short_r100_data(ifs_tco79_short_r100_reader):
    return ifs_tco79_short_r100_reader.retrieve()

@pytest.fixture(scope="session")
def ifs_tco79_short_r200_reader():
    return Reader(model="IFS", exp="test-tco79", source="short", loglevel=LOGLEVEL, regrid="r200")

@pytest.fixture(scope="session")
def ifs_tco79_short_r200_data(ifs_tco79_short_r200_reader):
    return ifs_tco79_short_r200_reader.retrieve()

# =============================================================================
# FESOM fixtures
# =============================================================================
@pytest.fixture(scope="session")
def fesom_test_pi_original_2d_reader():
    return Reader(model="FESOM", exp="test-pi", source="original_2d", loglevel=LOGLEVEL)

@pytest.fixture(scope="session")
def fesom_test_pi_original_2d_data(fesom_test_pi_original_2d_reader):
    return fesom_test_pi_original_2d_reader.retrieve(var='tos')

@pytest.fixture(scope="session")
def fesom_test_pi_original_2d_r200_fF_reader():
    return Reader(model="FESOM", exp="test-pi", source="original_2d",
                  regrid="r200", fix=False, loglevel=LOGLEVEL)

@pytest.fixture(scope="session")
def fesom_test_pi_original_2d_r200_fF_data(fesom_test_pi_original_2d_r200_fF_reader):
    return fesom_test_pi_original_2d_r200_fF_reader.retrieve()

# =============================================================================
# ICON fixtures
# =============================================================================
@pytest.fixture(scope="session")
def icon_test_healpix_short_reader():
    return Reader(model="ICON", exp="test-healpix", source="short", loglevel=LOGLEVEL)

@pytest.fixture(scope="session")
def icon_test_healpix_short_data(icon_test_healpix_short_reader):
    return icon_test_healpix_short_reader.retrieve(var='2t')

@pytest.fixture(scope="session")
def icon_test_r2b0_short_reader():
    return Reader(model="ICON", exp="test-r2b0", source="short", loglevel=LOGLEVEL)

@pytest.fixture(scope="session")
def icon_test_r2b0_short_data(icon_test_r2b0_short_reader):
    return icon_test_r2b0_short_reader.retrieve(var='t')

# =============================================================================
# NEMO fixtures
# =============================================================================
@pytest.fixture(scope="session")
def nemo_test_eORCA1_long_2d_reader():
    return Reader(model="NEMO", exp="test-eORCA1", source="long-2d", loglevel=LOGLEVEL)

@pytest.fixture(scope="session")
def nemo_test_eORCA1_long_2d_data(nemo_test_eORCA1_long_2d_reader):
    return nemo_test_eORCA1_long_2d_reader.retrieve(var='tos')

@pytest.fixture(scope="session")
def nemo_test_eORCA1_short_3d_reader():
    return Reader(model="NEMO", exp="test-eORCA1", source="short-3d", loglevel=LOGLEVEL)

@pytest.fixture(scope="session")
def nemo_test_eORCA1_short_3d_data(nemo_test_eORCA1_short_3d_reader):
    return nemo_test_eORCA1_short_3d_reader.retrieve(var='so')
