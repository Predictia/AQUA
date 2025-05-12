import os
import pytest
import shutil
import xarray as xr
import pandas as pd
from aqua import LRAgenerator, Reader

LOGLEVEL = "DEBUG"
LRAPATH = 'ci/IFS/test-tco79/r100/monthly'
LRAPATH_DAILY = 'ci/IFS/test-tco79/r100/daily'


@pytest.fixture(params=[{"model": "IFS", "exp": "test-tco79", "source": "long", "var": "2t", "outdir": "lra_test"}])
def lra_arguments(request):
    """Provides LRA generator arguments as a dictionary."""
    return request.param


@pytest.mark.aqua
class TestLRA:
    """Class containing LRA tests."""

    def test_definitive_false(self, lra_arguments, tmp_path):
        """Test LRA generator with definitive=False."""
        args = lra_arguments
        test = LRAgenerator(
            catalog='ci', model=args["model"], exp=args["exp"], source=args["source"],
            var=args["var"], outdir=args["outdir"], tmpdir=str(tmp_path),
            resolution='r100', frequency='monthly', loglevel=LOGLEVEL
        )

        test.retrieve()
        test.generate_lra()
        assert os.path.isdir(os.path.join(os.getcwd(), args["outdir"], LRAPATH))
        shutil.rmtree(os.path.join(args["outdir"]))

    @pytest.mark.parametrize("nworkers", [1, 2])
    def test_definitive_true(self, lra_arguments, tmp_path, nworkers):
        """Test LRA generator with definitive=True."""
        args = lra_arguments
        test = LRAgenerator(
            catalog='ci', model=args["model"], exp=args["exp"], source=args["source"],
            var=args["var"], outdir=args["outdir"], tmpdir=str(tmp_path),
            resolution='r100', frequency='monthly', definitive=True,
            loglevel=LOGLEVEL, nproc=nworkers
        )

        test.retrieve()
        test.data = test.data.sel(time="2020-01")
        test.generate_lra()

        file_path = os.path.join(os.getcwd(), args["outdir"], LRAPATH, "2t_test-tco79_r100_monthly_mean_202001.nc")
        test.check_integrity(varname=args["var"])
        assert os.path.isfile(file_path)

        file = xr.open_dataset(file_path)
        assert len(file.time) == 1
        assert pytest.approx(file['2t'][0, 1, 1].item()) == 248.0704
        shutil.rmtree(os.path.join(args["outdir"]))

    def test_regional_subset(self, lra_arguments, tmp_path):
        """Test LRA generator with regional subset."""
        args = lra_arguments
        region = {'name': 'europe', 'lon': [-10, 30], 'lat': [35, 70]}

        test = LRAgenerator(
            catalog='ci', model=args["model"], exp=args["exp"], source=args["source"],
            var=args["var"], outdir=args["outdir"], tmpdir=str(tmp_path),
            resolution='r100', frequency='daily', definitive=True,
            loglevel=LOGLEVEL, region=region
        )

        test.retrieve()
        test.data = test.data.sel(time="2020-01-20")
        test.generate_lra()

        file_path = os.path.join(os.getcwd(), args["outdir"], LRAPATH_DAILY, "2t_test-tco79_r100_daily_mean_europe_202001.nc")
        assert os.path.isfile(file_path)

        xfield = xr.open_dataset(file_path).where(lambda x: x.notnull(), drop=True)
        assert xfield.lat.min() > 35
        assert xfield.lat.max() < 70
        shutil.rmtree(os.path.join(args["outdir"]))

    def test_zarr_entry(self, lra_arguments, tmp_path):
        """Test LRA generator with Zarr archive creation."""
        args = lra_arguments
        test = LRAgenerator(
            catalog='ci', model=args["model"], exp=args["exp"], source=args["source"],
            var=args["var"], outdir=args["outdir"], tmpdir=str(tmp_path),
            resolution='r100', frequency='monthly', nproc=1,
            loglevel=LOGLEVEL, definitive=True
        )

        test.retrieve()
        test.generate_lra()
        test.create_catalog_entry()
        test.create_zarr_entry()

        reader1 = Reader(model=args["model"], exp=args["exp"], source='lra-r100-monthly')
        reader2 = Reader(model=args["model"], exp=args["exp"], source='lra-r100-monthly-zarr')

        data1 = reader1.retrieve()
        data2 = reader2.retrieve()
        assert data1.equals(data2)
        shutil.rmtree(os.path.join(args["outdir"]))

    def test_dask_overwrite(self, lra_arguments, tmp_path):
        """Test LRA generator with overwrite=True and Dask initialization."""
        args = lra_arguments
        test = LRAgenerator(
            catalog='ci', model=args["model"], exp=args["exp"], source=args["source"],
            var=args["var"], outdir=args["outdir"], tmpdir=str(tmp_path),
            resolution='r100', frequency='monthly', nproc=2,
            loglevel=LOGLEVEL, definitive=True, overwrite=True
        )

        test.retrieve()
        test.generate_lra()
        assert os.path.isdir(os.path.join(os.getcwd(), args["outdir"], LRAPATH))
        shutil.rmtree(os.path.join(args["outdir"]))

    def test_exclude_incomplete(self, lra_arguments, tmp_path):
        """Test LRA generator's exclude_incomplete option."""
        args = lra_arguments
        test = LRAgenerator(
            catalog='ci', model=args["model"], exp=args["exp"], source=args["source"],
            var=args["var"], outdir=args["outdir"], tmpdir=str(tmp_path),
            resolution='r100', frequency='monthly', definitive=True,
            loglevel=LOGLEVEL, exclude_incomplete=True
        )

        test.retrieve()
        test.generate_lra()

        missing_file = os.path.join(os.getcwd(), args["outdir"], LRAPATH, "2t_test-tco79_r100_monthly_mean_202008.nc")
        existing_file = os.path.join(os.getcwd(), args["outdir"], LRAPATH, "2t_test-tco79_r100_monthly_mean_202002.nc")

        assert not os.path.exists(missing_file)
        assert os.path.exists(existing_file)

        file = xr.open_dataset(existing_file)
        assert len(file.time) == 1
        test.check_integrity(varname=args["var"])
        shutil.rmtree(os.path.join(args["outdir"]))

    def test_concat_var_year(self, lra_arguments, tmp_path):
        """Test concatenation of monthly files into a single yearly file."""
        args = lra_arguments
        resolution = 'r100'
        frequency = 'monthly'
        year = 2022

        test = LRAgenerator(
            catalog='ci', model=args["model"], exp=args["exp"], source=args["source"],
            var=args["var"], outdir=args["outdir"], tmpdir=str(tmp_path),
            resolution=resolution, frequency=frequency, loglevel=LOGLEVEL
        )

        for month in range(1, 13):
            mm = f'{month:02d}'
            filename = test.get_filename(args["var"], year, month=mm)
            timeobj = pd.Timestamp(f'{year}-{mm}-01')
            ds = xr.Dataset({args["var"]: xr.DataArray([0], dims=['time'], coords={'time': [timeobj]})})
            ds.to_netcdf(filename)

        test._concat_var_year(args["var"], year)
        outfile = test.get_filename(args["var"], year)

        assert os.path.exists(outfile)
        shutil.rmtree(os.path.join(args["outdir"]))

    def test_concat_var_year_cdo(self, lra_arguments, tmp_path):
        """Test concatenation of monthly files into a single yearly file using cdo."""
        args = lra_arguments
        resolution = 'r100'
        frequency = 'monthly'
        year = 2022

        test = LRAgenerator(
            catalog='ci', model=args["model"], exp=args["exp"], source=args["source"],
            var=args["var"], outdir=args["outdir"], tmpdir=str(tmp_path), compact="cdo",
            resolution=resolution, frequency=frequency, loglevel=LOGLEVEL
        )

        for month in range(1, 13):
            mm = f'{month:02d}'
            filename = test.get_filename(args["var"], year, month=mm)
            timeobj = pd.Timestamp(f'{year}-{mm}-01')
            ds = xr.Dataset({args["var"]: xr.DataArray([0], dims=['time'], coords={'time': [timeobj]})})
            ds.to_netcdf(filename)

        test._concat_var_year(args["var"], year)
        outfile = test.get_filename(args["var"], year)

        assert os.path.exists(outfile)
        shutil.rmtree(os.path.join(args["outdir"]))