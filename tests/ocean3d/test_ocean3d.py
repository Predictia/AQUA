import os
import pytest
import xarray as xr
from aqua import Reader
from aqua.util import load_yaml, ConfigPath
from ocean3d import check_variable_name

from ocean3d import stratification
from ocean3d import mld

from ocean3d import hovmoller_plot
from ocean3d import time_series
from ocean3d import multilevel_trend
from ocean3d import zonal_mean_trend
from pathlib import Path

@pytest.fixture
def common_setup(tmp_path):
    """Fixture to set up common configuration and test data."""
    loglevel = 'warning'
    catalog = 'ci'
    exp = 'hpz3'
    model = 'FESOM'
    source = 'monthly-3d'
    region = 'Indian Ocean'
    output_dir = tmp_path
    output = True
    reader = Reader(model=model, exp=exp, source= source, catalog= catalog, regrid='r100')
    data = reader.retrieve(var=["thetao", "so"])
    data = reader.regrid(data)

    return {
        "loglevel": loglevel,
        "model": model,
        "exp": exp,
        "source": source,
        "data": data,
        "region": region,
        "output_dir" : output_dir,
        "output" : output
    }

# @pytest.mark.diagnostics
# def test_check_variable_name(common_setup):
#     """Test variable name checking and transformations."""
#     setup = common_setup
#     data = check_variable_name(setup["data"], loglevel=setup["loglevel"])
#     # Ensure required variables exist
#     assert 'so' in data, "Variable 'so' not found in dataset"
#     assert 'thetao' in data, "Variable 'thetao' not found in dataset"
#     assert data['thetao'].attrs.get('units') == 'degC', "Units not converted to Celsius"
#     assert 'lev' in data.dims, "Dimension 'lev' missing in dataset"

# # Hovmoller Function
# @pytest.fixture
# def hovmoller_instance(common_setup):
#     """Fixture to initialize hovmoller plot instance"""
#     setup = common_setup
#     setup["data"] = check_variable_name(setup["data"], loglevel=setup["loglevel"])
#     hovmoller_plot_init = hovmoller_plot(setup)
#     return hovmoller_plot_init
    
# @pytest.mark.diagnostics
# def test_hovmoller_data(hovmoller_instance):
#     """Test data loading for hovmoller plot."""
#     hovmoller_instance.data_for_hovmoller_lev_time_plot()
#     for i in range(1, len(hovmoller_instance.plot_info) + 1):
#         assert hovmoller_instance.plot_info[i]["data"] is not None, f"Data not loaded for hovmoller plot hovmoller_instance.plot_info[1]['type']"
    
# @pytest.mark.diagnostics
# def test_hovmoller_plot(hovmoller_instance):
#     """Test hovmoller plot generation."""
#     hovmoller_instance.plot()
    # output_file = Path(f"{time_series_instance.output_dir}/pdf/{time_series_instance.model}-{time_series_instance.exp}-{time_series_instance.source}_hovmoller_plots_indian_ocean.pdf")
#     assert output_file.exists(), "Plot not generated"
    
#Time_series Function
@pytest.fixture
def time_series_instance(common_setup):
    """Fixture to initialize time series plot instance"""
    setup = common_setup
    setup["data"] = check_variable_name(setup["data"], loglevel=setup["loglevel"])
    time_series_init = time_series(setup)
    return time_series_init

@pytest.mark.diagnostics
def test_time_series(time_series_instance):
    """Test data loading for time series plot."""
    time_series_instance.data_for_hovmoller_lev_time_plot()
    for i in range(1, len(time_series_instance.plot_info) + 1):
        assert time_series_instance.plot_info[i]["data"] is not None, f"Data not loaded for hovmoller plot hovmoller_instance.plot_info[1]['type']"
    
@pytest.mark.diagnostics
def test_time_series(time_series_instance):
    """Test time series plot generation."""
    time_series_instance.plot()
    output_file = Path(f"{time_series_instance.output_dir}/pdf/{time_series_instance.model}-{time_series_instance.exp}-{time_series_instance.source}_time_series_indian_ocean.pdf")
    assert output_file.exists(), "Plot not generated"