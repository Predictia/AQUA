import pytest
import numpy as np

# from aqua import aqua

from aqua import Reader, catalogue


def test_aqua_import():
    assert True


def test_aqua_catalogue():
    catalog = catalogue()
    assert len(catalog) > 0


def test_init():
    reader = Reader(model="FESOM", exp="test-pi", source="original_2d")
    assert reader.model == "FESOM"
    assert reader.exp == "test-pi"
    assert reader.source == "original_2d"


@pytest.fixture
def reader_instance():
    return Reader(model="FESOM", exp="test-pi", source="original_2d", regrid="r200")


def test_retrieve(reader_instance):
    data = reader_instance.retrieve(fix=False)
    assert len(data) > 0
    assert data.a_ice.shape == (2, 3140)


def test_regrid(reader_instance):
    data = reader_instance.retrieve(fix=False)
    sstr = reader_instance.regrid(data["sst"][0:2, :])
    assert sstr.shape == (2, 90, 180)
    assert np.nanmean(sstr[0, :, :].values) == pytest.approx(13.350324258783935)
    assert np.nanmean(sstr[1, :, :].values) == pytest.approx(13.319154700343551)


def test_fldmean(reader_instance):
    data = reader_instance.retrieve(fix=False)
    global_mean = reader_instance.fldmean(data.sst[:2, :])
    assert global_mean.shape == (2,)
    assert global_mean.values[0] == pytest.approx(17.99434183)
    assert global_mean.values[1] == pytest.approx(17.98060367)


@pytest.fixture(
    params=[
        ("IFS", "test-tco79", "original_2d", "r200", "tas"),
        ("FESOM", "test-pi", "original_2d", "r200", "sst"),
    ]
)
def reader_arguments(request):
    return request.param


def test_reader(reader_arguments):
    model, exp, source, regrid, variable = reader_arguments
    reader = Reader(model=model, exp=exp, source=source, regrid=regrid)
    data = reader.retrieve(fix=False)
    assert len(data) > 0
