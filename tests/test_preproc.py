import pytest
import xarray
from aqua import Reader

loglevel = "DEBUG"

@pytest.fixture(
    params=[
        ("IFS", "test-tco79", "short_masked", "2t", "r100")
    ]
)

def reader_arguments(request):
    return request.param

def double(x : xarray.Dataset) -> xarray.Dataset:
    return x * 2

@pytest.mark.aqua
class TestPreproc():
    """Test different preprocessing functions"""

    def test_preproc(self, reader_arguments):
        """
        Test if the masked source is correctly read
        """
        model, exp, source, variable, regrid = reader_arguments

        reader = Reader(model=model, exp=exp, source=source, regrid=regrid, loglevel=loglevel)
        data = reader.retrieve()
        
        reader_preproc = Reader(model=model, exp=exp, source=source, regrid=regrid,
                                preproc=double, loglevel=loglevel)
        data_preproc = reader_preproc.retrieve()

        assert (data[variable] * 2).equals(data_preproc[variable])