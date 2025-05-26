import pytest
from aqua.diagnostics.teleconnections import NAO, PlotNAO

# pytest approximation, to bear with different machines
approx_rel = 1e-4
loglevel = 'DEBUG'

@pytest.mark.diagnostics
def test_NAO():
    """
    Test that the NAO class works
    """
    init_dict = {
        'model': 'IFS',
        'exp': 'test-tco79',
        'source': 'teleconnections',
        'loglevel': loglevel
    }

    nao = NAO(**init_dict)
    nao.retrieve()

    assert nao.data is not None, "Data should not be None"

    nao.compute_index()
    assert nao.index is not None, "Index should not be None"
    assert nao.index[4].values == pytest.approx(0.21909582, rel=approx_rel)

    reg_DJF = nao.compute_regression(season='DJF')
    assert reg_DJF.isel(lon=4, lat=23).values == pytest.approx(80.99873476, rel=approx_rel)

    cor = nao.compute_correlation()
    assert cor.isel(lon=4, lat=23).values == pytest.approx(0.00220419, rel=approx_rel)

    init_dict_hpx = {
        'model': 'ERA5',
        'exp': 'era5-hpx3',
        'source': 'monthly',
        'loglevel': loglevel
    }

    nao_hpx = NAO(**init_dict_hpx)

    reg_DJF_hpx = nao_hpx.compute_regression(season='DJF')
    cor_hpx = nao_hpx.compute_correlation()

    plot_ref = PlotNAO(loglevel=loglevel, indexes=nao.index,
                       ref_indexes=nao_hpx.index)

    fig, _ = plot_ref.plot_index()
