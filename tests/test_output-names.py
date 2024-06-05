import os
import pytest
import xarray as xr
import matplotlib.pyplot as plt
from aqua.logger import log_configure
from aqua.util import OutputNamer  # Adjust this import to match your module's structure

# Initialize the logger for the tests
log_configure(log_level='DEBUG', log_name='OutputNamerTest')

@pytest.fixture
def output_namer():
    return OutputNamer(diagnostic='dummy', model='MSWEP', exp='past', loglevel='DEBUG', default_path='.')

def test_generate_name(output_namer):
    # Test filename generation without additional parameters
    filename = output_namer.generate_name(diagnostic_product='mean', suffix='nc')
    assert filename == 'dummy.mean.MSWEP.past.nc'
    
    # Test filename generation with additional parameters
    filename = output_namer.generate_name(diagnostic_product='mean', var='mtpr', model_2='ERA5', exp_2='era5', time_start='1990-01-01', time_end='1990-02-01', time_precision='ym', area='indian_ocean', frequency="3H", status="preliminary")
    assert filename == 'dummy.mean.mtpr.MSWEP.past.ERA5.era5.indian_ocean.199001.199002.frequency_3H.status_preliminary.nc'

def test_save_netcdf(output_namer):
    # Create a simple xarray dataset
    data = xr.Dataset({'data': (('x', 'y'), [[1, 2], [3, 4]])})
    
    # Test saving netCDF file without additional parameters
    path = output_namer.save_netcdf(dataset=data, diagnostic_product='mean')
    assert path == './dummy.mean.MSWEP.past.nc'
    
    # Test saving netCDF file with additional parameters
    path = output_namer.save_netcdf(dataset=data, diagnostic_product='mean', var='mtpr', model_2='ERA5', exp_2='era5', time_start='1990-01-01', time_end='1990-02-01', time_precision='ym', area='indian_ocean', frequency="3H", status="preliminary")
    assert path == './dummy.mean.mtpr.MSWEP.past.ERA5.era5.indian_ocean.199001.199002.frequency_3H.status_preliminary.nc'

def test_save_pdf(output_namer):
    # Create a simple matplotlib figure
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [4, 5, 6])
    
    # Test saving PDF file without additional parameters
    path = output_namer.save_pdf(fig=fig, diagnostic_product='mean')
    assert path == './dummy.mean.MSWEP.past.pdf'
    
    # Test saving PDF file with additional parameters
    path = output_namer.save_pdf(fig=fig, diagnostic_product='mean', var='mtpr', model_2='ERA5', exp_2='era5', time_start='1990-01-01', time_end='1990-02-01', time_precision='ym', area='indian_ocean', frequency="3H", status="preliminary")
    assert path == './dummy.mean.mtpr.MSWEP.past.ERA5.era5.indian_ocean.199001.199002.frequency_3H.status_preliminary.pdf'

def test_save_png(output_namer):
    # Create a simple matplotlib figure
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [4, 5, 6])
    
    # Test saving PNG file without additional parameters
    path = output_namer.save_png(fig=fig, diagnostic_product='mean')
    assert path == './dummy.mean.MSWEP.past.png'
    
    # Test saving PNG file with additional parameters
    path = output_namer.save_png(fig=fig, diagnostic_product='mean', var='mtpr', model_2='ERA5', exp_2='era5', time_start='1990-01-01', time_end='1990-02-01', time_precision='ym', area='indian_ocean', frequency="3H", status="preliminary")
    assert path == './dummy.mean.mtpr.MSWEP.past.ERA5.era5.indian_ocean.199001.199002.frequency_3H.status_preliminary.png'

def test_missing_diagnostic_product(output_namer):
    # Test that a ValueError is raised when diagnostic_product is not provided
    with pytest.raises(ValueError, match="The 'diagnostic_product' parameter is required and cannot be empty."):
        output_namer.generate_name()

    data = xr.Dataset({'data': (('x', 'y'), [[1, 2], [3, 4]])})
    with pytest.raises(ValueError, match="The 'diagnostic_product' parameter is required and cannot be empty."):
        output_namer.save_netcdf(dataset=data)

    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [4, 5, 6])
    with pytest.raises(ValueError, match="The 'diagnostic_product' parameter is required and cannot be empty."):
        output_namer.save_pdf(fig=fig)

    with pytest.raises(ValueError, match="The 'diagnostic_product' parameter is required and cannot be empty."):
        output_namer.save_png(fig=fig)

def test_metadata_addition(output_namer):
    # Create a simple xarray dataset and metadata
    data = xr.Dataset({'data': (('x', 'y'), [[1, 2], [3, 4]])})
    metadata = {'author': 'test', 'description': 'test metadata'}

    # Save netCDF file with metadata
    path = output_namer.save_netcdf(dataset=data, diagnostic_product='mean', metadata=metadata)
    loaded_data = xr.open_dataset(path)
    assert loaded_data.attrs['author'] == 'test'
    assert loaded_data.attrs['description'] == 'test metadata'

    # Create a simple matplotlib figure
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [4, 5, 6])
    
    # Save PDF file with metadata
    pdf_path = output_namer.save_pdf(fig=fig, diagnostic_product='mean', metadata=metadata)
    # Check metadata in PDF (this is more complex, requires reading PDF metadata, which is skipped here for simplicity)

def test_overwriting_files(output_namer):
    # Create a simple xarray dataset
    data = xr.Dataset({'data': (('x', 'y'), [[1, 2], [3, 4]])})

    # Save netCDF file with rebuild=True
    path = output_namer.save_netcdf(dataset=data, diagnostic_product='mean', rebuild=True)
    assert os.path.exists(path)

    # Modify the dataset and save with rebuild=False
    data['data'].values[0, 0] = 100
    output_namer.rebuild = False
    path_no_overwrite = output_namer.save_netcdf(dataset=data, diagnostic_product='mean')
    assert os.path.exists(path_no_overwrite)
    assert xr.open_dataset(path)['data'].values[0, 0] != 100  # Ensure the file was not overwritten

def test_invalid_figure_input(output_namer):
    # Test handling of invalid figure input
    with pytest.raises(ValueError, match="The provided fig parameter is not a valid matplotlib Figure or pyplot figure."):
        output_namer.save_pdf(fig="invalid_figure", diagnostic_product='mean')

    with pytest.raises(ValueError, match="The provided fig parameter is not a valid matplotlib Figure or pyplot figure."):
        output_namer.save_png(fig="invalid_figure", diagnostic_product='mean')
