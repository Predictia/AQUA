import pytest
import numpy as np
from aqua import Reader

@pytest.mark.parametrize('var',['2t','ttr'])
def test_timmean_monthly(var):
    """Timmean test for monthly aggregation"""
    reader = Reader(model="IFS", exp="test-tco79", source='long', freq='mon')
    data = reader.retrieve(fix=False)
    avg = reader.timmean(data[var])
    nmonths = len(np.unique(data.time.dt.month))
    unique, counts = np.unique(avg.time.dt.month, return_counts=True)
    assert avg.shape == (nmonths, 9, 18)
    assert len(unique) == nmonths
    assert all(counts == counts[0])

@pytest.mark.parametrize('var',['2t','ttr'])
def test_timmean_daily(var):
    """Timmean test for daily aggregation"""
    reader = Reader(model="IFS", exp="test-tco79", source='long', freq='day')
    data = reader.retrieve(fix=False)
    avg = reader.timmean(data[var])
    unique, counts = np.unique(avg.time.dt.day, return_counts=True)
    assert avg.shape == (197, 9, 18)
    assert len(unique) == 31
    assert all(counts == np.array([7, 7, 7, 6, 6, 6, 6, 6, 6, 6, 
                               6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7,
                               7, 7, 7, 7, 7, 7, 7, 6, 4]))
    
def test_timmean_monthly_reader():
    """Timmean test for monthly aggregation from Reader directly"""
    reader = Reader(model="IFS", exp="test-tco79", source='long', freq='mon')
    data = reader.retrieve(fix=False, timmean=True)
    nmonths = len(np.unique(data.time.dt.month))
    unique, counts = np.unique(data['2t'].time.dt.month, return_counts=True)
    assert data['2t'].shape == (nmonths, 9, 18)
    assert len(unique) == nmonths
    assert all(counts == counts[0])
