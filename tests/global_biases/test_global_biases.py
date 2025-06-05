import pytest
import os
import numpy as np
import xarray as xr
from aqua.diagnostics import GlobalBiases, PlotGlobalBiases

# Tolerance for numerical comparisons
approx_rel = 1e-4
loglevel = 'DEBUG'

tmp_path = "./"
var = 'q'
gb = GlobalBiases(catalog='ci', model='ERA5', exp='era5-hpz3', source='monthly', regrid='r100')
plotgb = PlotGlobalBiases()
gb.retrieve()

@pytest.mark.diagnostics
def test_climatology():
    gb.compute_climatology(var=var, seasonal=True)
    assert hasattr(gb, "climatology")
    assert hasattr(gb, "seasonal_climatology")
    assert isinstance(gb.climatology, xr.Dataset)
    assert isinstance(gb.seasonal_climatology, xr.Dataset)
    assert var in gb.climatology
    assert var in gb.seasonal_climatology
    assert "season" in gb.seasonal_climatology[var].dims
    assert set(gb.seasonal_climatology["season"].values) == {"DJF", "MAM", "JJA", "SON"}
    
    nc = os.path.join(tmp_path, 'netcdf', 'globalbiases.climatology.ci.ERA5.era5-hpz3.q.nc')
    assert os.path.exists(nc)

    nc_seasonal = os.path.join(tmp_path, 'netcdf', 'globalbiases.seasonal_climatology.ci.ERA5.era5-hpz3.q.nc')
    assert os.path.exists(nc_seasonal)

    plotgb.plot_climatology(data=gb.climatology, var=var, plev=85000)
    
    pdf = os.path.join(tmp_path, 'pdf', 'globalbiases.climatology.ci.ERA5.era5-hpz3.q.85000.pdf')
    assert os.path.exists(pdf)

    png = os.path.join(tmp_path, 'png', 'globalbiases.climatology.ci.ERA5.era5-hpz3.q.85000.png')
    assert os.path.exists(png)

@pytest.mark.diagnostics
def test_bias():
    plotgb.plot_bias(data=gb.climatology, data_ref=gb.climatology, var=var, plev=85000)
    pdf = os.path.join(tmp_path, 'pdf', 'globalbiases.bias.ci.ERA5.era5-hpz3.ERA5.era5-hpz3.q.85000.pdf')
    assert os.path.exists(pdf)
    png = os.path.join(tmp_path, 'png', 'globalbiases.bias.ci.ERA5.era5-hpz3.ERA5.era5-hpz3.q.85000.png')
    assert os.path.exists(png)

@pytest.mark.diagnostics
def test_seasonal_bias():
    plotgb.plot_seasonal_bias(data=gb.seasonal_climatology, data_ref=gb.seasonal_climatology, var=var, plev=85000)
    pdf = os.path.join(tmp_path, 'pdf', 'globalbiases.seasonal_bias.ci.ERA5.era5-hpz3.ERA5.era5-hpz3.q.85000.pdf')
    assert os.path.exists(pdf)
    png = os.path.join(tmp_path, 'png', 'globalbiases.seasonal_bias.ci.ERA5.era5-hpz3.ERA5.era5-hpz3.q.85000.png')
    assert os.path.exists(png)

@pytest.mark.diagnostics
def test_vertical_bias():
    plotgb.plot_vertical_bias(data=gb.climatology, data_ref=gb.climatology, var=var)
    pdf = os.path.join(tmp_path, 'pdf', 'globalbiases.vertical_bias.ci.ERA5.era5-hpz3.ERA5.era5-hpz3.q.pdf')
    assert os.path.exists(pdf)
    png = os.path.join(tmp_path, 'png', 'globalbiases.vertical_bias.ci.ERA5.era5-hpz3.ERA5.era5-hpz3.q.png')
    assert os.path.exists(png)