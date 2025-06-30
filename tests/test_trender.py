"""Test cases for the Trender class."""

import pytest
from aqua import Reader

loglevel = "DEBUG"

@pytest.mark.aqua
class TestTrender:
    """Test class for Trender functionality."""

    def test_coeffs_dataset(self):
        """Test for polynomial coefficients on Dataset"""

        reader = Reader(model="IFS", exp="test-tco79", source='long', loglevel='info')
        data = reader.retrieve()
        block1 = data.isel(time=slice(0, 1000))
        coeffs = reader.trender.coeffs(block1, degree=1)
        avg = coeffs['2t'].sel(degree=1).mean().values
        assert float(avg) == pytest.approx(-7.91903731e-17, rel=1e-5)
        coeffs = reader.trender.coeffs(block1, degree=1, normalize=True)
        avg = coeffs['2t'].sel(degree=1).mean().values
        assert float(avg) == pytest.approx(-0.0002850853431, rel=1e-5)


    def test_trend_dataarray(self):
        """Trivial test for trend on DataArray"""
        reader = Reader(model="IFS", exp="test-tco79", source='long', loglevel=loglevel)
        data = reader.retrieve()

        block1 = data['2t'].isel(time=slice(0, 1000))
        trend1 = reader.trender.trend(block1).aqua.fldmean()

        assert trend1.shape == (1000,)
        assert pytest.approx(trend1.values[300]) == 285.908

    def test_detrend_dataarray(self):
        """Trivial test for detrending on DataArray"""
        reader = Reader(model="IFS", exp="test-tco79", source='long', loglevel=loglevel)
        data = reader.retrieve()
        block1 = data['2t'].isel(time=slice(0, 1000))
        det1 = reader.detrend(block1).aqua.fldmean()

        assert det1.shape == (1000,)
        assert pytest.approx(det1.values[300]) == 0.3778275

    def test_detrend_dataset(self):
        """Second trivial test for detrending on Dataset"""
        reader = Reader(model="IFS", exp="test-tco79", source='long', loglevel=loglevel)
        data = reader.retrieve()
        block2 = data[['2t', 'skt']].isel(time=slice(0, 100))
        det2 = reader.detrend(block2, dim='time', degree=2)

        assert list(det2.data_vars) == ['2t', 'skt']
        assert pytest.approx(det2['skt'].isel(time=10, lon=2, lat=2).values) == -0.098381225331