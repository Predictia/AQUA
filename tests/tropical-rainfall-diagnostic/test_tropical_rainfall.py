"""Test of tropical rainfall diagnostic"""

import pytest
import numpy as np
import xarray

import re

from os import listdir
from os.path import isfile, join
from os import remove

from aqua import Reader
from aqua.util import create_folder

import sys
path_to_diagnostic='./diagnostics/tropical-rainfall-diagnostic/'
sys.path.insert(1, path_to_diagnostic)
from tropical_rainfall_class import TR_PR_Diagnostic as TR_PR_Diag


@pytest.mark.tropical_rainfall
@pytest.fixture(params=[
    Reader(model="ICON", exp="ngc2009", source="lra-r100-monthly"),
    Reader(model="IFS", exp="tco2559-ng5", source="lra-r100-monthly"),
    Reader(model="MSWEP", exp="past", source="monthly")
])

def reader(request):
    """Reader instance fixture"""
    data = request.param
    retrieved = data.retrieve()
    return retrieved.isel(time=slice(10,11))

@pytest.mark.tropical_rainfall
def test_module_import():
    """Testing the import of tropical rainfall diagnostic
    """
    try:
        from tropical_rainfall_class import TR_PR_Diagnostic as TR_PR_Diag
    except ModuleNotFoundError:
        assert False, "Diagnostic could not be imported"

@pytest.fixture
def check_precipitation_in_data(reader):
    data = reader
    try:
        data['tprate']
        return True
    except KeyError:
        print('Dataset not contains the precipitation rate')
        return False
    
@pytest.fixture
def data_size(reader):
    data = reader
    if 'DataArray' in str(type(data)):
        size = data.size
    elif 'Dataset' in str(type(data)): 
        names = list(data.dims) 
        size = 1
        for i in names:
            size *= data[i].size
    return size

@pytest.mark.tropical_rainfall
def test_update_default_attribute():
    """ Testing the update of default attributes
    """
    diag = TR_PR_Diag()
    old_trop_lat_value = diag.trop_lat
    diag.class_attributes_update(trop_lat=20)
    new_trop_lat_value = diag.trop_lat
    assert old_trop_lat_value != new_trop_lat_value

@pytest.fixture
def histogram_output(reader):
    """ Histogram output fixture
    """
    data = reader
    diag = TR_PR_Diag(num_of_bins = 20, first_edge = 0, width_of_bin = 1*10**(-6)/20)
    hist = diag.histogram(data)
    return hist


@pytest.mark.tropical_rainfall
def test_hisogram_counts(histogram_output, data_size): 
    """ Testing the histogram counts
    """
    hist = histogram_output
    assert sum(hist.counts.values) > 0 
    assert sum(hist.counts.values) < data_size

@pytest.mark.tropical_rainfall
def test_histogram_frequency(histogram_output): 
    """ Testing the histogram frequency
    """
    hist = histogram_output
    frequency_sum = sum(hist.frequency.values)
    assert  frequency_sum -1 < 10**(-4) 


@pytest.mark.tropical_rainfall
def test_histogram_pdf(histogram_output):
    """ Testing the histogram pdf
    """
    hist = histogram_output
    pdf_sum = sum(hist.pdf.values*hist.width.values)
    assert  pdf_sum-1 < 10**(-4) 


@pytest.mark.tropical_rainfall
def test_histogram_load_to_memory(histogram_output):
    """ Testing the histogram load to memory
    """
    path_to_save=str(path_to_diagnostic)+"/test_output/histograms/"
    create_folder(folder=str(path_to_diagnostic)+"test_output/", loglevel='WARNING')
    create_folder(folder=str(path_to_diagnostic)+"test_output/histograms/", loglevel='WARNING')
    
    # Cleaning the repository with histograms before new test
    histogram_list = [f for f in listdir(path_to_save) if isfile(join(path_to_save, f))]
    histograms_list_full_path = [str(path_to_save)+str(histogram_list[i]) for i in range(0, len(histogram_list))]
    for i in range(0, len(histograms_list_full_path)):
        remove(histograms_list_full_path[i])

    hist = histogram_output
    diag = TR_PR_Diag()
    diag.save_histogram(dataset=hist, path_to_save=path_to_save, name_of_file='test_hist_saving')
    files = [f for f in listdir(path_to_save) if isfile(join(path_to_save, f))]
    assert 'test_hist_saving' in files[0]

    time_band=hist.counts.attrs['time_band']
    try:
        re_time_band = re.split(":", re.split(", ", time_band)[0])[0]+'_' + re.split(":", re.split(", ", time_band)[1])[0] in files[0]
    except IndexError:
        re_time_band = re.split("'", re.split(":", time_band)[0])[1]
    assert re_time_band in time_band


@pytest.mark.tropical_rainfall
def test_units_convertation(reader):
    """ Testing the units convertation
    """ 
    data = reader 
    diag = TR_PR_Diag()
    data = diag.precipitation_units_converter(data, new_unit='m')
    assert data.tprate.attrs['units'] == 'm'
    

@pytest.mark.tropical_rainfall
def test_figure_load_to_memory(histogram_output):
    """ Testing the figure load to memory
    """
    create_folder(folder=str(path_to_diagnostic)+"test_output/plots/", loglevel='WARNING')
    path_to_save=str(path_to_diagnostic)+"/test_output/plots/"
    hist = histogram_output
    diag = TR_PR_Diag()
    diag.hist_figure(hist, path_to_save=str(path_to_save)+'test_fig_saving.png')
    files = [f for f in listdir(path_to_save) if isfile(join(path_to_save, f))]
    assert 'test_fig_saving.png' in files

    
@pytest.mark.tropical_rainfall
def test_lazy_mode_calculation(reader):
    """ Testing the lazy mode calculation
    """
    data = reader
    diag = TR_PR_Diag(num_of_bins = 20, first_edge = 0, width_of_bin = 1*10**(-6)/20)
    hist_lazy = diag.histogram(data, lazy=True)
    assert isinstance(hist_lazy, xarray.core.dataarray.DataArray) 
    assert 'time_band' not in hist_lazy.attrs
    assert 'lat_band'  not in hist_lazy.attrs
    assert 'lon_band'  not in hist_lazy.attrs

@pytest.mark.tropical_rainfall
def test_local_attributes_of_histogram(histogram_output):
    """ Testing the local attributes of histogram
    """
    hist = histogram_output
    assert 'time_band' in hist.counts.attrs
    assert 'lat_band' in hist.counts.attrs
    assert 'lon_band' in hist.counts.attrs

@pytest.mark.tropical_rainfall
def test_global_attributes_of_histogram(histogram_output):
    """ Testing the global attributes of histogram
    """
    hist = histogram_output
    try: 
        assert 'time_band' in hist.attrs['history']
        assert 'lat_band'  in hist.attrs['history']
        assert 'lon_band'  in hist.attrs['history']
    except KeyError:
        print(f"The obtained xarray.Dataset doesn't have global attributes.")

@pytest.mark.tropical_rainfall
def test_variables_of_histogram(histogram_output):
    """ Testing the variables of histogram
    
    """
    hist = histogram_output
    assert isinstance(hist, xarray.core.dataarray.Dataset) 
    try:
        hist.counts
    except KeyError:
        assert False, "counts not in variables"
    try:
        hist.frequency
    except KeyError:
        assert False, "frequency not in variables"   
    try:
        hist.pdf
    except KeyError:
        assert False, "pdfy not in variables"   


@pytest.mark.tropical_rainfall
def test_coordinates_of_histogram(histogram_output):
    """ Testing the coordinates of histogram
    """
    hist = histogram_output
    'center_of_bin' in  hist.coords
    'width' in  hist.coords

@pytest.mark.tropical_rainfall
def test_latitude_band(reader):
    """ Testing the latitude band
    """
    data = reader
    max_lat_value = max(data.lat.values[0], data.lat.values[-1])
    diag = TR_PR_Diag(trop_lat=10)
    data_trop = diag.latitude_band(data) 
    assert max_lat_value > max(data_trop.lat.values[0], data_trop.lat.values[-1])
    assert 10 > data_trop.lat.values[-1]


@pytest.mark.tropical_rainfall
def test_histogram_merge(histogram_output):
    """ Testing the histogram merge"""
    hist_1 = histogram_output
    counts_1= sum(hist_1.counts.values)
    
    hist_2 = histogram_output
    counts_2= sum(hist_2.counts.values)

    diag = TR_PR_Diag()

    path_to_save=str(path_to_diagnostic)+"/test_output/histograms/"
    diag.save_histogram(dataset=hist_2, path_to_save=path_to_save, name_of_file='test_merge')
    
    hist_merged = diag.merge_two_datasets(tprate_dataset_1=hist_1, tprate_dataset_2=hist_2)
    counts_merged= sum(hist_merged.counts.values)
    assert counts_merged==(counts_1+counts_2)

    #hist_merged_from_mem = diag.merge_list_of_histograms(path_to_histograms=path_to_save, all=True)
    #counts_merged_from_mem= sum(hist_merged_from_mem .counts.values)
    #assert counts_merged_from_mem==(counts_1+counts_2)

