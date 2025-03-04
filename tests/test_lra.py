import os
import shutil
import pytest
from datetime import datetime
import xarray as xr
from aqua import LRAgenerator, Reader

loglevel = "DEBUG"

@pytest.fixture(
    params=[("IFS", "test-tco79", "long", "2t", "lra_test", "tmpdir")]
)
def lra_arguments(request):
    return request.param

# path for lra data
lrapath = 'ci/IFS/test-tco79/r100/monthly'

@pytest.mark.aqua
class TestLRA():
    """Class for LRA Tests"""

    def test_definitive_false(self, lra_arguments):
        """Test the LRA generator with definitive = False"""
        model, exp, source, var, outdir, tmpdir = lra_arguments
        test = LRAgenerator(catalog='ci', model=model, exp=exp, source=source, var=var,
                            outdir=outdir, tmpdir=tmpdir, resolution='r100',
                            frequency='monthly', loglevel=loglevel)
        test.retrieve()
        test.generate_lra()
        assert os.path.isdir(os.path.join(os.getcwd(), outdir,
                                          lrapath))
        
    # defintiive = True with or without dask
    @pytest.mark.parametrize("nworkers", [1, 2])
    def test_definitive_true(self, lra_arguments, nworkers):
        """Test the LRA generator with definitive = True"""
        model, exp, source, var, outdir, tmpdir = lra_arguments
        test = LRAgenerator(catalog='ci', model=model, exp=exp, source=source, var=var,
                            outdir=outdir, tmpdir=tmpdir, resolution='r100',
                            frequency='monthly', definitive=True,
                            loglevel=loglevel, nproc=nworkers)
        test.retrieve()
        test.data = test.data.sel(time="2020-01")
        test.generate_lra()
        path = os.path.join(os.getcwd(), outdir,lrapath,
                            "2t_test-tco79_r100_monthly_202001.nc")
        test.check_integrity(varname=var)
        assert os.path.isfile(path)
        file = xr.open_dataset(path)
        assert len(file.time) == 1
        assert pytest.approx(file['2t'][0, 1, 1].item()) == 248.0704
        shutil.rmtree(os.path.join(os.getcwd(), outdir))

    def test_regional_subset(self, lra_arguments):
        """Test the LRA generator with regional subset"""
        model, exp, source, var, outdir, tmpdir = lra_arguments
        region = { 'name': 'europe', 'lon': [-10, 30], 'lat': [35, 70] }
        test = LRAgenerator(catalog='ci', model=model, exp=exp, source=source, var=var,
                            outdir=outdir, tmpdir=tmpdir, resolution='r100',
                            frequency='daily', definitive=True,
                            loglevel=loglevel, region=region)
        test.retrieve()
        test.data = test.data.sel(time="2020-01-20")
        test.generate_lra()
        lrapath2 = 'ci/IFS/test-tco79/r100/daily'
        path = os.path.join(os.getcwd(), outdir,lrapath2,
                            "2t_test-tco79_r100_daily_europe_202001.nc")
        assert os.path.isfile(path)
        xfield = xr.open_dataset(path)
        xfield = xfield.where(xfield.notnull(), drop=True)
        assert xfield.lat.min() > 35
        assert xfield.lat.max() < 70
        shutil.rmtree(os.path.join(os.getcwd(), outdir))
        
    # test with definitive = True and  catalog netcdf and zarr entry
    def test_zarr_entry(self, lra_arguments):
        """
        Test the LRA generator with definitive = True
        but with create zarr archive
        """
        model, exp, source, var, outdir, tmpdir = lra_arguments
        test = LRAgenerator(catalog='ci', model=model, exp=exp, source=source, var=var,
                            outdir=outdir, tmpdir=tmpdir,
                            resolution='r100', frequency='monthly', nproc= 1,
                            loglevel=loglevel, definitive=True)
        test.retrieve()
        test.generate_lra()
        test.create_catalog_entry()
        test.create_zarr_entry()
        reader1 = Reader(model=model, exp=exp, source='lra-r100-monthly')
        reader2 = Reader(model=model, exp=exp, source='lra-r100-monthly-zarr')
        data1 = reader1.retrieve()
        data2 = reader2.retrieve()
        assert data1.equals(data2)
        shutil.rmtree(os.path.join(os.getcwd(), tmpdir))    


    # test with definitive = True and overwrite=True but with dask init
    def test_dask_overwrite(self, lra_arguments):
        """
        Test the LRA generator with definitive = False
        but with dask init and catalog generator
        """
        model, exp, source, var, outdir, tmpdir = lra_arguments
        test = LRAgenerator(catalog='ci', model=model, exp=exp, source=source, var=var,
                            outdir=outdir, tmpdir=tmpdir, overwrite=True,
                            definitive=True,
                            resolution='r100', frequency='monthly', nproc=2,
                            loglevel=loglevel)
        test.retrieve()
        test.generate_lra()
        assert os.path.isdir(os.path.join(os.getcwd(), outdir, lrapath))
        shutil.rmtree(os.path.join(os.getcwd(), outdir))
        shutil.rmtree(os.path.join(os.getcwd(), tmpdir))

    
    def test_exclude_incomplete(self, lra_arguments):
        """Test exclude_incomplete option"""
        model, exp, source, var, outdir, tmpdir = lra_arguments
        test = LRAgenerator(catalog='ci', model=model, exp=exp, source=source, var=var,
                            outdir=outdir, tmpdir=tmpdir, resolution='r100',
                            frequency='monthly', definitive=True, exclude_incomplete=True,
                            loglevel=loglevel)
        test.retrieve()
        test.generate_lra()

        path = os.path.join(os.getcwd(), outdir, lrapath,
                            "2t_test-tco79_r100_monthly_202008.nc")
        assert not os.path.exists(path)

        path = os.path.join(os.getcwd(), outdir, lrapath,
                            "2t_test-tco79_r100_monthly_202002.nc")
        assert os.path.exists(path)
        file = xr.open_dataset(path)
        assert len(file.time) == 1

        test.check_integrity(varname=var)
        assert os.path.isfile(path)
        shutil.rmtree(os.path.join(os.getcwd(), outdir))

    def test_concat_var_year(self, lra_arguments):
        """"
        Test the concatenation of monthly files into a single file for a year
        """

        # create a LRAgenerator object
        model, exp, source, var, outdir, tmpdir = lra_arguments
        resolution='r100'
        frequency='monthly'
        year = 2022
        test = LRAgenerator(catalog='ci', model=model, exp=exp, source=source, var=var,
                        outdir=outdir, tmpdir=tmpdir, resolution=resolution,
                        frequency=frequency, loglevel=loglevel)

        # Create temporary files for each month of the year
        for month in range(1, 13):
            mm = f'{month:02d}'
            filename =  test.get_filename(var, year, month = mm)
            timestr = f'{year}-{mm}-01'
            timeobj = datetime.strptime(timestr, "%Y-%m-%d")
            ds = xr.Dataset({
                var: xr.DataArray([0], dims=['time'], coords={'time': [timeobj]})
            })
            ds.to_netcdf(filename)

        test._concat_var_year(var, year)
        outfile = test.get_filename(var, year)

        # Check if a single file is created for the year
        assert os.path.exists(outfile)

        # cleaning 
        os.remove(outfile)
        shutil.rmtree(outdir)
