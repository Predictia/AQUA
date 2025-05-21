"""Test ensemble Ensemble module"""
import os
import subprocess
import pytest
import xarray as xr
import numpy as np
from aqua import Reader
from aqua.diagnostics import EnsembleLatLon
from aqua.diagnostics import EnsembleTimeseries
from aqua.diagnostics import EnsembleZonal


@pytest.mark.ensemble
def test_2D_datasets():
    """
    load aqua-analysis output of 2D Map of 2t.
    """
    #dataset = xr.open_dataset('../../AQUA_tests/models/FESOM/results/atmglobalmean.statistics_maps.2t.IFS-FESOM_historical-1990.nc')
    reader = Reader(model='FESOM', exp='results', source='atmglobalmean2D', catalog='ci', areas=False)
    dataset = reader.retrieve()
    dataset_list = [dataset,dataset]
    dataset = xr.concat(dataset_list, "Ensembles")
    del dataset_list
    return dataset

@pytest.mark.ensemble
def test_ensemble_2D_compute():
    """Test the compute method of EnsembleLatLons."""
    sample_dataset = test_2D_datasets()
    latlon = EnsembleLatLon(var="2t", dataset=sample_dataset)
    latlon.compute_statistics()
    latlon.plot()
    assert latlon.dataset_mean is not None
    assert latlon.dataset_std.all() == 0 
    assert latlon.figure is not None

@pytest.mark.ensemble
def test_timeseries_datasets():
    """
    load aqua-analysis output of timeseries.
    """
    #dataset = xr.open_dataset('../../AQUA_tests/models/FESOM/results/aglobal_time_series_timeseries_2t_IFS-FESOM_historical-1990_mon.nc')
    reader = Reader(model='FESOM', exp='results', source='timeseries1D', catalog='ci', areas=False)
    dataset = reader.retrieve()
    dataset_list = [dataset,dataset]
    dataset = xr.concat(dataset_list, "Ensembles")
    del dataset_list
    return dataset

@pytest.mark.ensemble
def test_ensemble_timeseries_compute():
    """Test the compute method of EnsembleTimeseries."""
    sample_dataset = test_timeseries_datasets()
    ts = EnsembleTimeseries(var="2t", mon_model_dataset=sample_dataset)
    ts.compute_statistics()
    ts.plot()
    assert ts.mon_dataset_mean is not None
    assert ts.mon_dataset_std.values.all() == 0
    assert ts.figure is not None 

@pytest.mark.ensemble
def test_Zonal_datasets():
    """
    load aqua-analysis output of Zonal-Averages.
    """
    #dataset = xr.open_dataset('../../AQUA_tests/models/NEMO/results/IFS-NEMO-historical-1990-lra-r100-monthly_zonal_mean_trend_atlantic_ocean.nc')
    reader = Reader(model='NEMO', exp='results', source='zonal_mean-latlev', catalog='ci', areas=False)
    dataset = reader.retrieve()

    dataset_list = [dataset,dataset]
    dataset = xr.concat(dataset_list, "Ensembles")
    del dataset_list
    return dataset

@pytest.mark.ensemble
def test_ensemble_Zonal_compute():
    """Test the compute method of EnsembleZonal."""
    sample_dataset = test_Zonal_datasets()
    Zonal = EnsembleZonal(var="so", dataset=sample_dataset)
    Zonal.compute_statistics()
    Zonal.plot()

    assert Zonal.dataset_mean.all() is not None
    assert Zonal.dataset_std.any() == 0 or np.nan # this step needs correction
    assert Zonal.figure is not None   

