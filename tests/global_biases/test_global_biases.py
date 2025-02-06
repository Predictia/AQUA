import pytest
import numpy as np
import xarray as xr
from aqua import Reader
from aqua.diagnostics import GlobalBiases

# pytest approximation, to bear with different machines
approx_rel = 1e-4
loglevel = 'DEBUG'

@pytest.mark.global_biases
def test_global_biases():
    """
    Test for GlobalBiases diagnostic
    """
    exp = 'era5-hpz3'
    reader1 = Reader(model='ERA5', exp=exp, source='monthly', catalog='ci', regrid='r100')
    reader2 = Reader(model='ERA5', exp=exp, source='monthly', catalog='ci', regrid='r100')

    data1 = reader1.retrieve()
    data2 = reader2.retrieve()

    data1 = reader1.regrid(data1)
    data2 = reader2.regrid(data2)

    global_biases = GlobalBiases(data=data1, data_ref=data2, var_name='2t', loglevel=loglevel)

    fig, ax, bias = global_biases.plot_bias(vmin=None, vmax=None)
    assert fig is not None
    assert ax is not None

    assert np.allclose(np.nanmean(bias.values), 0, atol=approx_rel)