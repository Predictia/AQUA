import pytest
import numpy as np
import xarray as xr
from aqua.diagnostics import SeaIce, Plot2DSeaIce

approx_rel = 1e-4
loglevel = 'DEBUG'

# --- constants that match the ones you asked us to re-use --------------------#
CATALOG   = "ci"
MODEL     = "FESOM"
EXP       = "hpz3"
SOURCE    = "monthly-2d"
REGIONS   = ["arctic", "antarctic"]
LOGLEVEL  = "warning"
STARTDATE = "1991-01-01"
ENDDATE   = "2000-01-01"
REGRID    = "r100"

# ----------------------------  shared fixtures  ------------------------------#
@pytest.fixture(scope="session")
def frac_model_ds() -> xr.Dataset:
    """Sea-ice fraction for the model (both hemispheres)."""
    seaice = SeaIce(catalog=CATALOG, model=MODEL, exp=EXP, source=SOURCE,
                    startdate=STARTDATE, enddate=ENDDATE, regions=REGIONS, regrid=REGRID, loglevel=LOGLEVEL )
    return seaice.compute_seaice(method="fraction", var="siconc")

@pytest.fixture(scope="session")
def frac_ref_ds_arctic() -> xr.Dataset:
    """Arctic reference (fraction)."""
    seaice = SeaIce(model="OSI-SAF", exp="osi-450", source="nh-monthly",
                    startdate=STARTDATE, enddate=ENDDATE, regions="arctic", regrid=REGRID, loglevel=LOGLEVEL )
    return seaice.compute_seaice(method="fraction", var="siconc")

@pytest.fixture(scope="session")
def frac_ref_ds_antarctic() -> xr.Dataset:
    """Antarctic reference (fraction)."""
    seaice = SeaIce(model="OSI-SAF", exp="osi-450", source="sh-monthly",
                    startdate=STARTDATE, enddate=ENDDATE, regions="antarctic", regrid=REGRID, loglevel=LOGLEVEL )
    return seaice.compute_seaice(method="fraction", var="siconc")

@pytest.fixture(scope="session")
def thick_model_ds() -> xr.Dataset:
    """Sea-ice thickness for the model (both hemispheres)."""
    seaice = SeaIce(catalog=CATALOG, model=MODEL, exp=EXP, source=SOURCE,
                    startdate=STARTDATE, enddate=ENDDATE, regions=REGIONS, regrid=REGRID, loglevel=LOGLEVEL )
    return seaice.compute_seaice(method="thickness", var="siconc")

@pytest.fixture(scope="session")
def thick_ref_ds_arctic() -> xr.Dataset:
    """Arctic reference (thickness)."""
    seaice = SeaIce(model="OSI-SAF", exp="osi-450", source="nh-monthly",
                    startdate=STARTDATE, enddate=ENDDATE, regions="arctic", regrid=REGRID, loglevel=LOGLEVEL )
    return seaice.compute_seaice(method="thickness", var="siconc")

@pytest.fixture(scope="session")
def thick_ref_ds_antarctic() -> xr.Dataset:
    """Antarctic reference (thickness)."""
    seaice = SeaIce(model="OSI-SAF", exp="osi-450", source="sh-monthly",
                    startdate=STARTDATE, enddate=ENDDATE, regions="antarctic", regrid=REGRID, loglevel=LOGLEVEL )
    return seaice.compute_seaice(method="thickness", var="siconc")

@pytest.fixture(scope="session")
def projkw():
    """Orthographic projection matching your notebook."""
    return {"projname": "orthographic",
            "projpars": {"central_longitude": 0.0, "central_latitude": "max_lat_signed"}}

@pytest.fixture(scope="session")
def projkw_extent():
    """Azimuthal_equidistant projection matching your notebook."""
    return {'projpars': {'central_longitude': 0.0, 'central_latitude': 'max_lat_signed'},
            'extent_regions': {'Arctic': [-180, 180, 50, 90], 'Antarctic': [-180, 180, -50, -90]},
            'projname': 'azimuthal_equidistant'}

@pytest.mark.diagnostics
class TestData:
    @pytest.mark.parametrize(
        "bad_input", 
        ["string", 123]
    )
    def test_rejects_invalid_types(self, bad_input):
        p2d = Plot2DSeaIce(loglevel="DEBUG")
        with pytest.raises(TypeError):
            p2d._handle_data(bad_input)

    def test_accepts_dataset_or_dataarray(self, frac_model_ds):
        p2d = Plot2DSeaIce(loglevel="DEBUG")
        out = p2d._handle_data(frac_model_ds)
        assert isinstance(out, list)
        assert out and isinstance(out[0], xr.DataArray)

    @pytest.mark.parametrize(
        "meth", ["fraction", "thickness"]
    )
    def test_mask_ice_at_mid_lats(self, meth):
        """Basic sanity check for the masking helper."""
        lat = xr.DataArray(np.linspace(-90, 90, 181), dims="lat")
        lon = xr.DataArray(np.linspace(0, 359, 360), dims="lon")
        data = xr.DataArray(
            np.random.rand(181, 360),
            coords={"lat": lat, "lon": lon},
            dims=("lat", "lon"),
            attrs={"AQUA_method": meth, "AQUA_region": "arctic"},
        )
        p2d = Plot2DSeaIce()
        p2d.method = meth
        masked = p2d._mask_ice_at_mid_lats(data)

        if meth == "thickness":
            # mid-latitudes AND tiny thickness values should be turned to NaN
            assert masked.sel(lat=0.0, method="nearest").isnull().all()
        else:
            # for fraction, mid-latitudes are overwritten with zeros (no NaNs)
            mids = masked.where((lat >= -45) & (lat <= 40), drop=True)
            assert not mids.isnull().any()

@pytest.mark.diagnostics
class TestPlot2DSeaIce:
    """Tests for the Plot2DSeaIce class."""

    @pytest.mark.parametrize(
        ("plot_type", "projkw_param"),
        [("var", "projkw"),  ("bias", "projkw_extent")],
    )
    def test_plot_runs_fract(self, plot_type, projkw_param, frac_model_ds, frac_ref_ds_arctic, frac_ref_ds_antarctic, projkw, projkw_extent):
        p2d = Plot2DSeaIce(ref=[frac_ref_ds_antarctic, frac_ref_ds_arctic],
                           models=frac_model_ds)

        projkw_value = projkw if projkw_param == "projkw" else projkw_extent
        p2d.plot_2d_seaice(
            plot_type=plot_type, projkw=projkw_value,
            plot_ref_contour=True,
            save_pdf=False, save_png=False )

    @pytest.mark.parametrize(
        ("plot_type", "projkw_param"),
        [("var", "projkw"),("bias", "projkw_extent") ],
    )
    def test_plot_runs_thick(self, plot_type, projkw_param, thick_model_ds, thick_ref_ds_arctic, thick_ref_ds_antarctic, projkw, projkw_extent):
        p2d = Plot2DSeaIce(ref=[thick_ref_ds_antarctic, thick_ref_ds_arctic],
                           models=thick_model_ds)

        projkw_value = projkw if projkw_param == "projkw" else projkw_extent
        p2d.plot_2d_seaice(plot_type=plot_type,projkw=projkw_value,
                           plot_ref_contour=True, save_pdf=False, save_png=False,
        )

    @pytest.mark.parametrize(
        ("bad_months", "exception"),
        [([0], ValueError), (["Feb"], TypeError)],
    )
    def test_bad_months_raise(self, bad_months, exception, frac_model_ds, projkw):
        p2d = Plot2DSeaIce(models=frac_model_ds)
        with pytest.raises(exception):
            p2d.plot_2d_seaice(
                months=bad_months, projkw=projkw,
                save_pdf=False, save_png=False,
            )

    def test_detect_common_regions_auto_detection(self, frac_model_ds, frac_ref_ds_arctic, frac_ref_ds_antarctic):
        """Test automatic region detection without specifying regions_to_plot when regions_to_plot is None."""
        p2d = Plot2DSeaIce(ref=[frac_ref_ds_antarctic, frac_ref_ds_arctic],
                           models=frac_model_ds,
                           regions_to_plot=None,  # This triggers _detect_common_regions
                           loglevel="DEBUG")
        
        # Check that regions were automatically detected
        assert p2d.regions_to_plot is not None
        assert len(p2d.regions_to_plot) > 0
        # Should detect both arctic and antarctic regions
        assert "arctic" in p2d.regions_to_plot or "Arctic" in p2d.regions_to_plot
        assert "antarctic" in p2d.regions_to_plot or "Antarctic" in p2d.regions_to_plot

    @pytest.mark.parametrize("method", ["fraction", "thickness"])
    def test_get_cmap_methods(self, method, frac_model_ds):
        """Test colormap generation for different sea ice methods."""
        p2d = Plot2DSeaIce(models=frac_model_ds, loglevel="DEBUG")
        p2d.method = method
        
        # Get a sample data array
        sample_data = frac_model_ds[0] if isinstance(frac_model_ds, list) else frac_model_ds        
        cmap_dict = p2d._get_cmap(sample_data)
        
        assert 'colormap' in cmap_dict
        
        if method == 'fraction':
            assert cmap_dict['norm'] is None  # fraction uses default normalization
            assert cmap_dict['boundaries'] is None
        elif method == 'thickness':
            assert cmap_dict['norm'] is not None  # thickness uses BoundaryNorm
            assert cmap_dict['boundaries'] is not None
            assert len(cmap_dict['boundaries']) > 0

    def test_set_projpars_function_registry(self, frac_model_ds):
        """Test projection parameter processing with function registry."""
        p2d = Plot2DSeaIce(models=frac_model_ds, loglevel="DEBUG")
        
        # Set up test data with known lat values
        test_data = frac_model_ds[0] if isinstance(frac_model_ds, list) else frac_model_ds
        
        p2d.projpars = {'central_longitude': 0.0,
                        'central_latitude': 'max_lat_signed'}
        
        # Mock the data to have known lat values
        p2d.reg_ref = [test_data]
        
        result = p2d._set_projpars()

        assert 'central_latitude' in result
        assert isinstance(result['central_latitude'], (int, float))
        
        # Test with invalid function name
        p2d.projpars = {'central_latitude': 'invalid_function_name'}
        
        result = p2d._set_projpars()
        assert 'central_latitude' not in result  # Invalid function should be skipped    

    @pytest.mark.parametrize(
        ("param_name", "param_value"),
        [
        ("plot_type", "unknown"), ("method", "invalid")
        ],
    )
    def test_bad_parameters_raise(self, param_name, param_value, frac_model_ds, projkw):
        p2d = Plot2DSeaIce(models=frac_model_ds)
        with pytest.raises(ValueError):
            kwargs = {param_name: param_value, "projkw": projkw, "save_pdf": False, "save_png": False}
            p2d.plot_2d_seaice(**kwargs)

    def test_plot_saves_outputs_to_tmp(self, tmp_path,
                                    frac_model_ds, frac_ref_ds_arctic, frac_ref_ds_antarctic, projkw):
        """Ensure that both PNG and PDF files are saved correctly in a temp directory."""
        
        # Initialize with temp directory
        p2d = Plot2DSeaIce(ref=[frac_ref_ds_antarctic, frac_ref_ds_arctic],
                           models=frac_model_ds, 
                         outdir=str(tmp_path), loglevel="INFO")

        p2d.plot_2d_seaice(plot_type="var",projkw=projkw, save_pdf=True, save_png=True, months=[3])

        # Check for presence of at least one PNG and one PDF
        saved_files = list(tmp_path.rglob("*.png")) + list(tmp_path.rglob("*.pdf"))

        assert any(f.suffix == ".png" for f in saved_files), "No PNG file saved."
        assert any(f.suffix == ".pdf" for f in saved_files), "No PDF file saved."