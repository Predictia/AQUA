"""Tests for ocean3d diagnostics"""

import os
import pytest
from aqua import Reader
from aqua.util import load_yaml, ConfigPath
from ocean3d import check_variable_name

@pytest.fixture
def common_setup(tmp_path):
    """Fixture to set up common configuration and data for tests."""
    Configurer = ConfigPath()
    loglevel = 'warning'
    exp = 'era5-hpz3'
    reader = Reader(model='ERA5', exp=exp, source='monthly', catalog='ci', regrid='r100')
    data = reader.retrieve()
    data = reader.regrid(data)

    return {
        "config": config,
        "loglevel": loglevel,
        "outputdir": tmp_path,
        "data": data,
        "exp": exp
    }
    
    
@pytest.mark.ocean3d
def test_check_variable_name(common_setup):
    setup = common_setup
    print(setup)
    data = check_variable_name(setup["data"], loglevel=setup["loglevel"])
    
    # Verify that the required variables are in the dataset
    assert 'so' in data
    assert 'thetao' in data
    
    # Verify that the units have been converted to degrees Celsius
    assert data['thetao'].attrs['units'] == 'degC'
    
    # Verify that the dimensions have been renamed
    assert 'lev' in data.dims

    print("Test passed successfully!")