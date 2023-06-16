"""Test of tropical rainfall diagnostic"""

import pytest
import numpy as np
from aqua import Reader
import sys

sys.path.insert(0, '../../diagnostics/tropical-rainfall-diagnostic/')
from tropical_rainfall_class import TR_PR_Diagnostic as TR_PR_Diag

@pytest.fixture(params=[
    #Reader(model="ICON", exp="ngc2009", source="lra-r100-monthly"),
    #Reader(model="IFS", exp="tco2559-ng5", source="lra-r100-monthly"),
    Reader(model="MSWEP", exp="past", source="monthly")
])

def reader(request):
    """Reader instance fixture"""
    data = request.param
    retrieved = data.retrieve()
    return data, retrieved  

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

@pytest.mark.tropical_rainfall
def test_hisogram_counts(reader):
    """ Testing the histogram counts
    """
    data = reader
    data = data.isel(time=10)
    diag = TR_PR_Diag(num_of_bins = 20, first_edge = 0, width_of_bin = 1*10**(-6)/20)
    hist = diag.histogram(data)
    assert sum(hist.counts) > 0 
    assert sum(hist.counts) < data_size

@pytest.mark.tropical_rainfall
def test_histogram_frequency(reader):
    """ Testing the histogram frequency
    """
    data = reader
    data = data.isel(time=10)
    diag = TR_PR_Diag(num_of_bins = 20, first_edge = 0, width_of_bin = 1*10**(-6)/20)
    hist = diag.histogram(data)
    frequency_sum = sum(hist.frequency.values)
    assert  frequency_sum -1 < 10**(-4) 


@pytest.mark.tropical_rainfall
def test_histogram_pdf(reader):
    """ Testing the histogram pdf
    """
    data = reader
    data = data.isel(time=10)
    diag = TR_PR_Diag(num_of_bins = 20, first_edge = 0, width_of_bin = 1*10**(-6)/20)
    hist = diag.histogram(data)
    pdf_sum = sum(hist.frequency.values*hist.width.values)
    assert  pdf_sum-1 < 10**(-4) 


@pytest.mark.tropical_rainfall
def test_histogram_load_to_memory():
    """ Testing the histogram load to memory
    """
   #...
    
@pytest.mark.tropical_rainfall
def test_units_convertation():
    """ Testing the units convertation
    """
    #...:

@pytest.mark.tropical_rainfall
def test_figure_load_to_memory():
    """ Testing the figure load to memory
    """
   #...
    
@pytest.mark.tropical_rainfall
def test_lazy_mode_calculation():
    """ Testing the lazy mode calculation
    """
    #...::

@pytest.mark.tropical_rainfall
def test_local_attributes_of_histogram():
    """ Testing the local attributes of histogram
    """
    #...:::

@pytest.mark.tropical_rainfall
def test_global_attributes_of_histogram():
    """ Testing the global attributes of histogram
    """
    #...:::_

@pytest.mark.tropical_rainfall
def test_name_of_histogram():
    """ Testing the name of histogram
    """
    #...:::_


@pytest.mark.tropical_rainfall
def test_variables_of_histogram():
    """ Testing the variables of histogram
    
    """
    #...:::_

@pytest.mark.tropical_rainfall
def test_coordinates_of_histogram():
    """ Testing the coordinates of histogram
    """
    #...:::_

@pytest.mark.tropical_rainfall
def test_latitude_band():
    """ Testing the latitude band
    """
    #...:::_"""

@pytest.mark.tropical_rainfall
def test_time_band():
    """ Testing the time band
    """
    #...:::_

@pytest.mark.tropical_rainfall
def test_histogram_merge():
    """ Testing the histogram merge"""