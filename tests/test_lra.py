import pytest
import os, shutil
import xarray as xr
from aqua import LRAgenerator

@pytest.fixture(
    params=[("IFS", "test-tco79", "long", "2t", "lra_test")]
)

def lra_arguments(request):
    return request.param

@pytest.mark.aqua
class TestLRA():
    #test with definitive = False
    def test_definitive_false(self, lra_arguments):
            model, exp, source, var, outdir = lra_arguments
            test = LRAgenerator(model=model, exp=exp, source=source, var=var, outdir=outdir, 
                                resolution='r100', frequency='monthly')
            test.retrieve()
            test.generate_lra()
            assert os.path.isdir(os.path.join(os.getcwd(), outdir, "IFS/test-tco79/r100/monthly"))

    #test with definitive = True
    def test_definitive_true(self, lra_arguments):
            model, exp, source, var, outdir = lra_arguments
            test = LRAgenerator(model=model, exp=exp, source=source, var=var, outdir=outdir, 
                                resolution='r100', frequency='monthly', definitive = True)
            test.retrieve()
            year = test.data.sel(time=test.data.time.dt.year == 2020)
            month = year.sel(time=year.time.dt.month == 1)
            test.data = month
            test.generate_lra()
            path = os.path.join(os.getcwd(), outdir, "IFS/test-tco79/r100/monthly/2t_test-tco79_r100_monthly_2020.nc")
            assert os.path.isfile(path)    
            file = xr.open_dataset(path)
            assert len(file.time) == 1
            assert pytest.approx(file['2t'][0,1,1].item()) == 248.0704
            shutil.rmtree(os.path.join(os.getcwd(), outdir))
