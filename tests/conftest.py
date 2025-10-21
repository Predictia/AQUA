"""
Shared fixtures for AQUA test suite.
These fixtures use scope="session" to retrieve data once and share across all tests.
Reference: https://docs.pytest.org/en/stable/reference/fixtures.html
"""
import pytest
from aqua import Reader

LOGLEVEL = "DEBUG"

# Helper fixtures for common test settings
@pytest.fixture(scope="session")
def approx_rel():
    """Standard relative approximation for tests"""
    return 1e-4

@pytest.fixture
def fxt_loglevel():
    """Standard log level for tests (function scope for flexibility)"""
    return LOGLEVEL

# =============================================================================
# IFS test-tco79 fixtures
# =============================================================================

@pytest.fixture(scope="session")
def ifs_tco79_short_reader():
    """IFS test-tco79 short source reader - used by multiple test files"""
    return Reader(model="IFS", exp="test-tco79", source="short", loglevel=LOGLEVEL)

@pytest.fixture(scope="session")
def ifs_tco79_short_data(ifs_tco79_short_reader):
    """IFS test-tco79 short data - shared across test_fldstat, test_accessor, etc."""
    return ifs_tco79_short_reader.retrieve()

@pytest.fixture(scope="session")
def ifs_tco79_short_data_2t(ifs_tco79_short_reader):
    """IFS test-tco79 short data with only 2t variable"""
    return ifs_tco79_short_reader.retrieve(var='2t')

