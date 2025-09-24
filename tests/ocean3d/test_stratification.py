import pytest
from aqua.diagnostics.ocean_stratification.stratification import Stratification

approx_rel = 1e-3

@pytest.mark.diagnostics
def test_stratification():
    """Test the stratification class."""
    # Create an instance of the stratification class
    strat = Stratification(catalog='ci', model='FESOM',
                          exp='hpz3', source='monthly-3d',
                          regrid='r100', loglevel='DEBUG')

    strat.run(
        dim_mean=["lat","lon"],
        var=['thetao', 'so'],
        region='ls',
        mld=True,
        )
    data = strat.data.sel(month=12)
    assert strat is not None, "strat instance should not be None"
    assert data["mld"].values == pytest.approx(13.76194609,rel=approx_rel)
    assert data["rho"].isel(level=1).values == pytest.approx(26.63128532,rel=approx_rel)
