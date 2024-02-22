import pytest
from aqua import Reader

loglevel = "DEBUG"

@pytest.mark.aqua
def test_detrend():
    """Trivial test for detrending"""

    reader = Reader(model="IFS", exp="test-tco79", source='long', loglevel=loglevel)
    data = reader.retrieve(var=['2t','skt'])
    
    block1 = data['2t'].isel(time=slice(0,1000))
    det1 = reader.detrend(block1).aqua.fldmean()

    assert det1.shape == (1000,)
    assert pytest.approx(det1.values[300]) == 0.377827

    block2 = data[['2t','skt']].isel(time=slice(0,100))
    det2 = reader.detrend(block2, dim='time', degree=2)
    
    assert list(det2.data_vars) == ['2t','skt']
    assert det2['skt'].isel(time=10, lon=2, lat=2).values == -0.0983