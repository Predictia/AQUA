"""Testing if fldmean method works"""

import pytest
from aqua import Reader, FldStat

LOGLEVEL = "DEBUG"


@pytest.mark.aqua
class TestFldModule():
    """Class for fldmean standalone"""

    def test_fldmean_from_data(self):
        """test Fldmean class native from data"""

        reader = Reader(catalog='ci', model='IFS', exp='test-tco79',
                        source='short', regrid='r100', rebuild=True)
        data = reader.retrieve()
        fldmodule = FldStat(area=reader.src_grid_area.cell_area, loglevel=LOGLEVEL)
        assert fldmodule.fldmean(data)['2t'].size == 2
        fldmodule = FldStat(loglevel=LOGLEVEL)
        assert fldmodule.fldmean(data)['2t'].size == 2

    def test_fldmean_from_data_selection(self):
        """test Fldmean class native from data with reversed lat"""

        reader = Reader(catalog='ci', model='IFS', exp='test-tco79', 
                        source='long', regrid='r100', rebuild=True)
        data = reader.retrieve(var='2t')
        reverted = data.reindex({'lat': list(reversed(data.coords['lat']))})
        reverted = reverted.isel(time=slice(0, 3))
        fldmodule = FldStat(area=reader.src_grid_area.cell_area, loglevel=LOGLEVEL)
        assert fldmodule.fldmean(reverted)['2t'].size == 3

    def test_fldmean_raise(self):
        """test Fldmean class raise error if no area provided"""
        with pytest.raises(ValueError, match="Area must be an xarray DataArray or Dataset."):
            FldStat(loglevel=LOGLEVEL, area='pippo')

@pytest.mark.aqua
class TestFldmean():
    """Test class for fldmean"""

    @pytest.mark.parametrize(('source,value,shape'),
                             [('short', 285.75920, 2),
                             ('short_nn', 285.75920, 2),
                             ('long', 285.86724, 20)])
    def test_fldmean_ifs(self, source, value, shape):
        """Fldmean test for IFS"""
        reader = Reader(model="IFS", exp="test-tco79", source=source, loglevel=LOGLEVEL)
        data = reader.retrieve()
        if source == 'long':
            data = data.isel(time=slice(0, 20))
        avg = reader.fldmean(data['2t']).values
        assert avg.shape == (shape,)
        # assert avg[0] == pytest.approx(285.96816)
        assert avg[1] == pytest.approx(value)

    def test_fldmean_fesom(self):
        """Fldmean test for FESOM"""
        reader = Reader(model="FESOM", exp="test-pi", source='original_2d', loglevel=LOGLEVEL)
        data = reader.retrieve()
        avg = reader.fldmean(data['tos']).values
        assert avg.shape == (2,)
        # assert avg[1] == pytest.approx(17.9806)
        assert avg[1] == pytest.approx(291.1306)

    def test_fldmean_fesom_selection(self):
        """Fldmean test for FESOM"""
        reader = Reader(model="FESOM", exp="test-pi", source='original_2d',
                        regrid='r100', loglevel=LOGLEVEL)
        data = reader.retrieve()
        data = reader.regrid(data)
        avg = reader.fldmean(data['tos'], lon_limits=[50, 90], lat_limits=[10, 40]).values
        assert avg.shape == (2,)
        # assert avg[1] == pytest.approx(17.9806)
        assert avg[1] == pytest.approx(300.1865)

    def test_fldmean_healpix(self):
        """Fldmean test for FESOM"""
        reader = Reader(model="ICON", exp="test-healpix", source='short', loglevel=LOGLEVEL)
        data = reader.retrieve()
        avg = reader.fldmean(data['2t']).values
        assert avg.shape == (2,)
        assert avg[1] == pytest.approx(286.1479)

    def test_fldmean_healpix_selection(self):
        """Fldmean test for FESOM with area selection"""
        reader = Reader(model="ICON", exp="test-healpix", source='short',
                        regrid='r200', loglevel=LOGLEVEL)
        data = reader.retrieve()
        data = reader.regrid(data)
        avg = reader.fldmean(data['2t'],  lon_limits=[-30, 50], lat_limits=[-30, -90])
        assert "Area selection: lat=[-90, -30], lon=[330, 50]" in avg.history
        assert avg.values.shape == (2,)
        assert avg.values[0] == pytest.approx(285.131484)

    def test_fldmean_healpix_selection_lat_only(self):
        """Fldmean test for FESOM with area selection, only lat"""
        reader = Reader(model="ICON", exp="test-healpix", source='short',
                        regrid='r200', loglevel=LOGLEVEL)
        data = reader.retrieve()
        data = reader.regrid(data)
        avg = reader.fldmean(data['2t'], lat_limits=[-30, 30]).values
        assert avg.shape == (2,)
        assert avg[0] == pytest.approx(292.6823)

    def test_fldmean_icon(self):
        """Fldmean test for ICON"""
        reader = Reader(model="ICON", exp="test-r2b0", source='short', loglevel=LOGLEVEL)
        data = reader.retrieve()
        avg = reader.fldmean(data['t']).values
        assert avg.shape == (2, 90)
        assert avg[1, 1] == pytest.approx(214.4841)

    def test_fldmean_regridded(self):
        """Fldmean test for regridded data"""
        reader = Reader(model='FESOM', exp='test-pi', source='original_2d',
                        regrid='r250', loglevel=LOGLEVEL)
        data = reader.retrieve()
        avg = reader.fldmean(data['tos']).values
        assert avg.shape == (2,)
        assert avg[1] == pytest.approx(291.1306)

    def test_fldmean_nemo(self):
        """Fldmean test for NEMO"""
        reader = Reader(model="NEMO", exp="test-eORCA1", source='long-2d', loglevel=LOGLEVEL)
        data = reader.retrieve()
        avg = reader.fldmean(data['tos']).values
        assert avg.shape == (6,)
        assert avg[5] == pytest.approx(290.5516)

    def test_fldmean_nemo_3d(self):
        """Fldmean test for NEMO-3D"""
        reader = Reader(model="NEMO", exp="test-eORCA1", source='short-3d', loglevel=LOGLEVEL)
        data = reader.retrieve()
        avg = reader.fldmean(data['so']).values
        assert avg.shape == (8,)
        assert avg[4] == pytest.approx(34.63406)

@pytest.mark.aqua
class TestFldStatDims():
    """Test class for dims parameter functionality"""

    def test_fldmean_custom_dims_icon(self):
        """Test fldmean with custom dims parameter on ICON grid"""
        reader = Reader(model="ICON", exp="test-r2b0", source='short', loglevel=LOGLEVEL)
        data = reader.retrieve()
        fldmodule = FldStat(area=reader.src_grid_area.cell_area, loglevel=LOGLEVEL)
        
        # Test with explicit horizontal dims (should be ['cell'] for ICON)
        result = fldmodule.fldmean(data['t'], dims=['cell'])
        assert result.shape == (2, 90)  # time, height levels
        assert result.values[1, 1] == pytest.approx(214.4841)  # Same value as existing test

    def test_fldmean_partial_dims_icon_3d(self):
        """Test fldmean with subset of horizontal dims on 3D data"""
        reader = Reader(model="ICON", exp="test-r2b0", source='short', loglevel=LOGLEVEL)
        data = reader.retrieve()
        fldmodule = FldStat(area=reader.src_grid_area.cell_area, loglevel=LOGLEVEL)
        
        # Test averaging over only spatial dimension, keeping height
        result = fldmodule.fldmean(data['t'], dims=['cell'])
        # Should preserve height dimension but average over space
        assert 'level_full' in result.dims
        assert 'cell' not in result.dims
        assert result.shape == (2, 90)

    def test_fldmean_dims_validation_icon(self):
        """Test dims validation with ICON data"""
        reader = Reader(model="ICON", exp="test-r2b0", source='short', loglevel=LOGLEVEL)
        data = reader.retrieve()
        fldmodule = FldStat(area=reader.src_grid_area.cell_area, loglevel=LOGLEVEL)
        
        # Test invalid dimension
        with pytest.raises(ValueError, match="Dimension invalid_dim not found in horizontal dimensions"):
            fldmodule.fldmean(data['t'], dims=['invalid_dim'])

    def test_fldmean_dims_default_vs_explicit_icon(self):
        """Test that default and explicit dims give same results on ICON"""
        reader = Reader(model="ICON", exp="test-r2b0", source='short', loglevel=LOGLEVEL)
        data = reader.retrieve()
        fldmodule = FldStat(area=reader.src_grid_area.cell_area, loglevel=LOGLEVEL)
        
        # Compare default behavior with explicit dims
        result_default = fldmodule.fldmean(data['t'])
        result_explicit = fldmodule.fldmean(data['t'], dims=['cell'])
        
        # Results should be identical
        assert result_default.equals(result_explicit)
        assert result_default.values[1, 1] == pytest.approx(214.4841)

    def test_fldmean_dims_not_list(self):
        """Test that dims must be a list"""
        reader = Reader(model="ICON", exp="test-r2b0", source='short', loglevel=LOGLEVEL)
        data = reader.retrieve()
        fldmodule = FldStat(area=reader.src_grid_area.cell_area, loglevel=LOGLEVEL)
        
        with pytest.raises(ValueError, match="dims must be a list of dimension names."):
            fldmodule.fldmean(data['t'], dims='cell')