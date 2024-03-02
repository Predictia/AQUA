import pytest
import os

from aqua import Reader
from aqua.graphics import plot_single_map, plot_single_map_diff

loglevel = "DEBUG"


@pytest.mark.graphics
class TestSingleMap:
    """Basic tests for the Single map functions"""
    def setup_method(self):
        reader = Reader(model="FESOM", exp="test-pi", source="original_2d",
                        regrid="r200", fix=False, loglevel=loglevel)
        self.data = reader.retrieve(var='sst')

    def test_plot_single_map(self):
        """
        Test the plot_single_map function
        """
        plot_data = self.data["sst"].isel(time=0).aqua.regrid()
        fig, ax = plot_single_map(data=plot_data,
                                  save=True,
                                  nlevels=5,
                                  vmin=-2.0,
                                  vmax=30.0,
                                  outputdir='tests/figures/',
                                  cmap='viridis',
                                  gridlines=True,
                                  display=False,
                                  return_fig=True,
                                  title='Test plot',
                                  cbar_label='Sea surface temperature [°C]',
                                  dpi=100,
                                  model='FESOM',
                                  exp='test-pi',
                                  filename='test_single_map',
                                  format='png',
                                  nxticks=5,
                                  nyticks=5,
                                  loglevel=loglevel)
        assert fig is not None
        assert ax is not None

        # Check the file was created
        assert os.path.exists('tests/figures/test_single_map.png')

    def test_plot_single_map_diff(self):
        """
        Test the plot_single_map_diff function
        """
        plot_data = self.data["sst"].isel(time=0).aqua.regrid()
        plot_data2 = self.data["sst"].isel(time=1).aqua.regrid()
        fig, ax = plot_single_map_diff(data=plot_data,
                                       data_ref=plot_data2,
                                       save=True,
                                       nlevels=5,
                                       vmin_fill=-5.0,
                                       vmax_fill=5.0,
                                       sym=False,
                                       vmin_contour=-2.0,
                                       vmax_contour=30.0,
                                       outputdir='tests/figures/',
                                       cmap='viridis',
                                       gridlines=True,
                                       display=False,
                                       return_fig=True,
                                       title='Test plot',
                                       cbar_label='Sea surface temperature [°C]',
                                       dpi=100,
                                       model='FESOM',
                                       exp='test-pi',
                                       filename='test_single_map_diff',
                                       format='png',
                                       nxticks=5,
                                       nyticks=5,
                                       loglevel=loglevel)
        assert fig is not None
        assert ax is not None

        # Check the file was created
        assert os.path.exists('tests/figures/test_single_map_diff.png')
