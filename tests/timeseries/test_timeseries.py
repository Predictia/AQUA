import os
import pytest
import xarray as xr
from aqua.diagnostics.timeseries import Timeseries

# pytest approximation, to bear with different machines
approx_rel = 1e-4
loglevel = 'DEBUG'


@pytest.mark.timeseries
class TestTimeseries:
    """
    Test that the timeseries class works
    """

    def setup_method(self):
        """Initialize variables before each test."""
        self.catalog = 'ci'
        self.model = 'ERA5'
        self.exp = 'era5-hpz3'
        self.source = 'monthly'
        self.var = 'tcc'
        self.region = 'tropics'
        self.regrid = 'r100'

    def test_no_region(self):
        ts = Timeseries(catalog=self.catalog, model=self.model, exp=self.exp, source=self.source,
                        region=None, loglevel=loglevel, regrid=self.regrid)

        assert ts.lon_limits is None
        assert ts.lat_limits is None

    def test_wrong_region(self):
        with pytest.raises(ValueError):
            Timeseries(catalog=self.catalog, model=self.model, exp=self.exp, source=self.source,
                       region='topolinia', loglevel=loglevel, regrid=self.regrid)

    def test_monthly_annual_with_region(self, tmp_path):
        ts = Timeseries(catalog=self.catalog, model=self.model, exp=self.exp, source=self.source,
                        region=self.region, loglevel=loglevel, startdate='19900101', enddate='19911231',
                        regrid=self.regrid)

        assert ts.lon_limits == [-180, 180]
        assert ts.lat_limits == [-15, 15]

        ts.retrieve(var=self.var)
        assert isinstance(ts.data, xr.DataArray)

        ts.compute(freq='monthly')
        assert ts.monthly.values[0] == pytest.approx(60.145472982004186, rel=approx_rel)

        ts.save_netcdf(freq='monthly', outputdir=tmp_path)
        file = os.path.join(tmp_path, 'netcdf', 'timeseries.tcc.ci.ERA5.era5-hpz3.nc')
        assert os.path.exists(file)

        ts.compute(freq='annual')
        assert ts.annual.values[0] == pytest.approx(60.31101797654943, rel=approx_rel)

        ts.save_netcdf(freq='annual', outputdir=tmp_path)

    def test_hourly_daily_with_region(self):
        ts = Timeseries(catalog=self.catalog, model=self.model, exp=self.exp, source=self.source,
                        region=self.region, loglevel=loglevel, startdate='19900101', enddate='19900102',
                        regrid=self.regrid)

        ts.retrieve(var=self.var)

        ts.compute(freq='hourly')
        assert ts.hourly.values[0] == pytest.approx(60.145472982004186, rel=approx_rel)

        ts.compute(freq='daily')
        assert ts.daily.values[0] == pytest.approx(60.145472982004186, rel=approx_rel)

    def test_formula(self):
        ts = Timeseries(catalog=self.catalog, model=self.model, exp=self.exp, source=self.source,
                        region=self.region, loglevel=loglevel, startdate='19940101', enddate='19950101',
                        regrid=self.regrid)

        ts.retrieve(var='2*tcc', formula=True, standard_name='2tcc', long_name='2*Total Cloud Cover', units='%')

        ts.compute(freq='monthly')
        assert ts.monthly.values[0] ==  pytest.approx(120.29094596400837, rel=approx_rel)
        assert ts.monthly.values[-1] == pytest.approx(120.29094596400837, rel=approx_rel)
