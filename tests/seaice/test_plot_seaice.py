import pytest 
import xarray as xr
from aqua.diagnostics import SeaIce, PlotSeaIce
from aqua.util import OutputSaver

# pytest approximation, to bear with different machines
approx_rel = 1e-4
loglevel = 'DEBUG'

# Set up test parameters
catalog = 'ci'
model = 'FESOM'
exp ='hpz3'
source ='monthly-2d'
regions = ['arctic', 'antarctic']
loglevel = 'warning'
startdate = "1991-01-01"
enddate = "2000-01-01"
regrid = "r100"

@pytest.fixture(scope="session")
def siext() -> xr.Dataset:
    seaice = SeaIce(catalog=catalog, model=model, exp=exp, source=source, 
                    startdate=startdate, enddate=enddate,  regions=regions, regrid=regrid, loglevel=loglevel)
    return seaice.compute_seaice(method='extent', var='siconc')

@pytest.fixture(scope="session")
def siext_seas() -> xr.Dataset:
    seaice = SeaIce(catalog=catalog, model=model, exp=exp, source=source, 
                    startdate=startdate, enddate=enddate,  regions=regions, regrid=regrid, loglevel=loglevel)
    return seaice.compute_seaice(method='extent', var='siconc', get_seasonal_cycle=True)

@pytest.mark.diagnostics
class TestPlotSeaIce:
    """Tests for the PlotSeaIce class."""
    
    @pytest.mark.parametrize(
        ('datain', 'expect_exception'),
        [
        ('string',  ValueError),
        (123,       ValueError),
        ([1, 2, 3], ValueError),
        (None, None), # valid, returns None
        ]
    )
    def test_check_as_datasets_list(self, datain, expect_exception, siext):
        """Validate the _check_as_datasets_list utility."""
        plot_seaice = PlotSeaIce()

        # Adjust incoming param so that we actually feed a Dataset for the happy path
        datain = siext if datain is None else datain

        if expect_exception:
            with pytest.raises(expect_exception):
                plot_seaice._check_as_datasets_list(datain)
            return

        result = plot_seaice._check_as_datasets_list(datain)
        assert isinstance(result, list)
        assert result and isinstance(result[0], xr.Dataset)

    @pytest.mark.parametrize(
        ('regions_to_plot', 'expected_regions'),
        [
        (None,       ['Arctic', 'Antarctic']),
        (['Arctic'], ['Arctic']), # filter keeps only arctic
        ]
    )
    def test_repack_datasetlists(self, regions_to_plot, expected_regions, siext):
        """Ensure repacking preserves structure and obeys region filtering."""
        psi = PlotSeaIce(monthly_models=siext, regions_to_plot=regions_to_plot)
        repacked = psi.repacked_dict

        assert 'extent' in repacked     # method key
        method_block = repacked['extent']
        assert sorted(method_block.keys()) == sorted(expected_regions)

        for reg in expected_regions:
            assert method_block[reg]['monthly_models']    # non-empty list

    @pytest.mark.parametrize(
        ('regions_to_plot', 'expect_exception'),
        [
        ('arctic', TypeError),
        (123, TypeError),
        ]
    )
    def test_invalid_regions_type(self, regions_to_plot, expect_exception, siext):
        """regions_to_plot must be list or None."""
        with pytest.raises(expect_exception):
            PlotSeaIce(monthly_models=siext, regions_to_plot=regions_to_plot)  # not a list!

    def test_plot_timeseries_nosave_fig(self, siext):
        """Test the timeseries path with no files saved."""
        psi = PlotSeaIce(
            monthly_models=siext,
            monthly_ref=siext,
            regions_to_plot=['Arctic', 'Antarctic'],
            model=model, exp=exp, source=source,
            catalog=catalog, loglevel=loglevel
        )
        psi.plot_seaice(plot_type='timeseries', save_pdf=False, save_png=False)

    def test_plot_seaice_seasonal_cycle(self, siext):
        """Test the seasonal cycle path with no files saved."""
        psi = PlotSeaIce(
            regions_to_plot=['Arctic', 'Antarctic'],
            model=model, exp=exp, source=source,
            catalog=catalog, loglevel=loglevel
        )
        psi.plot_seaice(plot_type="seasonal_cycle", save_pdf=False, save_png=False)

    def test_plot_seascycle_multi(self, siext, siext_seas):
        """Test the seasonal cycle path with no files saved."""
        psi = PlotSeaIce(monthly_models=siext_seas,
                 monthly_ref=[siext_seas],
                 )
        psi.plot_seaice(plot_type="seasonal_cycle", save_pdf=False, save_png=False)

    def test_invalid_plot_type_raises(self, siext):
            psi = PlotSeaIce(monthly_models=siext)
            with pytest.raises(ValueError):
                psi.plot_seaice(plot_type='bad_type', save_pdf=False, save_png=False)

@pytest.mark.diagnostics
class TestPlotSeaIceExtras:
    # _get_region_name_in_datarray  
    @pytest.mark.parametrize(
        ("da", "expected"),
        [
        ( xr.DataArray( [0, 1, 2], dims="time", attrs={"AQUA_region": "CustomReg"}, name="dummy"),"CustomReg"),
        ( xr.DataArray([5, 6], dims="time", name="siext_Antarctic"), "Antarctic", ),
        ],
    )
    def test_get_region_name_ok(self, da, expected):
        psi = PlotSeaIce()
        assert psi._get_region_name_in_datarray(da) == expected

    def test_get_region_name_missing_raises(self):
        da = xr.DataArray([7, 8], dims="time")  # no attrs, no region in name
        psi = PlotSeaIce()
        with pytest.raises(KeyError):
            psi._get_region_name_in_datarray(da)

    # _gen_labelname & _getdata_fromdict  
    def _dummy_da(self, label):
        """Helper: make a one-point DataArray with AQUA_* attrs."""
        return xr.DataArray(
            [1],
            dims="time",
            attrs={"AQUA_model": label, "AQUA_exp": "e", "AQUA_source": "s"},
            name=f"var_{label}",
        )

    def test_gen_labelname_single_and_list(self):
        psi = PlotSeaIce()
        da = self._dummy_da("m1")
        assert psi._gen_labelname(da) == "m1 e s"

        da_list = [self._dummy_da("m1"), self._dummy_da("m2")]
        labels = psi._gen_labelname(da_list)
        assert labels == ["m1 e s", "m2 e s"]

    @pytest.mark.parametrize(
        ("dct", "expected_type"),
        [
        ({"key": [xr.DataArray([0], dims="t")]}, xr.DataArray),  # single -> DA
        ({"key": [xr.DataArray([0], dims="t"), xr.DataArray([1], dims="t")]}, list),  # multi -> list
        ({}, type(None)),  # missing -> None
        ],
    )
    def test_getdata_fromdict_variants(self, dct, expected_type):
        psi = PlotSeaIce()
        out = psi._getdata_fromdict(dct, "key")
        assert isinstance(out, expected_type) or out is None

    # save_fig branch (monkey-patch OutputSaver)  
    def test_save_fig_calls_output_saver(self, siext, monkeypatch):
        png_called = {"flag": False}
        pdf_called = {"flag": False}

        # fake save_png/pdf that just flips flags 
        def fake_png(self, *args, **kwargs):
            png_called["flag"] = True

        def fake_pdf(self, *args, **kwargs):
            pdf_called["flag"] = True

        monkeypatch.setattr(OutputSaver, "save_png", fake_png, raising=True)
        monkeypatch.setattr(OutputSaver, "save_pdf", fake_pdf, raising=True)

        psi = PlotSeaIce(monthly_models=siext,
                         regions_to_plot=["Arctic"], 
                         model=model, exp=exp, source=source, 
                         catalog=catalog, loglevel=loglevel )

        # Both branches inside save_fig should run 
        psi.plot_seaice(plot_type="timeseries", save_pdf=True, save_png=True)

        assert png_called["flag"] is True
        assert pdf_called["flag"] is True
