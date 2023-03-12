import pytest

# from aqua import aqua

from aqua import Reader, catalogue


def test_aqua_import():
    assert True


def test_aqua_catalogue():
    catalog = catalogue()
    assert len(catalog) > 0


@pytest.fixture(
    params=[
        ("IFS", "test-tco2559", "ICMGG_atm2d", "r200", "2t"),
        # ("IFS", "tco2559-ng5", "ICMU_atm3d", "r200"),
        # ("FESOM", "tco2559-ng5", "interpolated_global2d", "r200"),
        ("FESOM", "test-ng5", "original_2d", "r200", "ssh"),
        # ("FESOM", "tco2559-ng5", "original_3d", "r200"),
        # ("ICON", "ngc2009", "atm_2d_ml_R02B09"),
        # ("ICON", "ngc2009", "oce_200m_atmgrid"),
    ]
)
def reader_arguments(request):
    return request.param


def test_reader(reader_arguments):
    model, exp, source, regrid, variable = reader_arguments
    reader = Reader(model=model, exp=exp, source=source, regrid=regrid)
    data = reader.retrieve(fix=False)
    assert len(data) > 0
    # tasr = reader.regrid(data[variable][0:2, :])
    # assert tasr[0, :, :].values.mean() == pytest.approx(277.3602686711421)
    # assert tasr[1, :, :].values.mean() == pytest.approx(277.1929510385794)
