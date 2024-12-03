import pytest
from aqua.exceptions import NoDataError
from aqua.diagnostics import Teleconnection

# pytest approximation, to bear with different machines
approx_rel = 1e-4
loglevel = 'DEBUG'

telecname = 'ENSO'
model = 'IFS'
exp = 'test-tco79'
source = 'teleconnections'
interface = 'teleconnections-ci'


@pytest.mark.teleconnections
def test_class_ENSO():
    """
    Test that the ENSO class works
    """
    telec = Teleconnection(model=model, exp=exp, source=source,
                           loglevel=loglevel, telecname=telecname,
                           interface=interface)

    telec.evaluate_index()
    assert telec.index[4].values == pytest.approx(-1.08063012, rel=approx_rel)

    reg = telec.evaluate_regression()
    assert reg.isel(lon=4, lat=23).values == pytest.approx(-0.13339995,
                                                           rel=approx_rel)

    cor = telec.evaluate_correlation()
    assert cor.isel(lon=4, lat=23).values == pytest.approx(-0.06538111,
                                                           rel=approx_rel)

    cor_msl = telec.evaluate_correlation(var='msl')
    assert cor_msl.isel(lon=4, lat=23).values == pytest.approx(-0.18467891,
                                                               rel=approx_rel)


@pytest.mark.teleconnections
def test_teleconnections_retrieve():
    """Test exceptions in the Teleconnection class"""
    telec = Teleconnection(model=model, exp=exp, source=source,
                           loglevel=loglevel, telecname=telecname,
                           interface=interface, regrid='r100')

    with pytest.raises(NoDataError):
        telec.retrieve(var='pippo')

    telec.retrieve()

    assert telec.data[telec.var].isel(time=0,
                                      lon=10, lat=10).values == pytest.approx(245.42805154,
                                                                              rel=approx_rel)


@pytest.mark.teleconnections
def test_teleconnections_unknown():
    """Test unknown teleconnection"""
    with pytest.raises(ValueError):
        Teleconnection(model=model, exp=exp, source=source,
                       loglevel=loglevel, telecname='pippo',
                       interface=interface)
