""" PlotSeaIce doc """
import os
import xarray as xr
from matplotlib import pyplot as plt

from aqua.diagnostics.core import Diagnostic
from aqua.diagnostics import GlobalBiases, PlotGlobalBiases
from aqua.exceptions import NoDataError, NotEnoughDataError
from aqua.logger import log_configure, log_history
from aqua.util import ConfigPath, OutputSaver

from .util import extract_dates

xr.set_options(keep_attrs=True)

class Plot2DSeaIce:
    """ A class for processing and visualizing surface maps and 
    biases of sea ice fraction or thickness. """

    def __init__(self,
                 models=None,
                 ref=None,
                 model: str = None, exp: str = None, source: str = None, catalog: str = None,
                 regions_to_plot: list = None, # ['Arctic', 'Antarctic'], # this is a list of strings with the region names to plot

                 outdir='./',
                 rebuild=True,
                 dpi=300, loglevel='WARNING'):

        # logging setup
        self.loglevel = loglevel
        self.logger = log_configure(log_level=self.loglevel, log_name='Plot2DSeaIce')

        self.ref = ref
        self.models = models

        self.catalog = catalog
        self.model = model
        self.exp = exp
        self.source = source

        self.regions_to_plot = check_list_regions_type(regions_to_plot, logger=self.logger)

        self.outdir  = outdir
        self.rebuild = rebuild
        self.dpi = dpi

    def _collect_models_data(self) -> list:
        """
        Normalize `self.models` and return a flat list of xarray.DataArray objects.
        Handles the following cases:
            - A single xarray.Dataset: includes all its data variables (data_vars)
            - A single xarray.DataArray: includes the DataArray itself
            - A list or tuple of either type (mixed allowed)
        """
        if self.models is None:
            return None
        
        models_list = [self.models] if isinstance(self.models, (xr.Dataset, xr.DataArray)) else self.models

        data_arrays = []
        
        for model in models_list:
            if isinstance(model, xr.Dataset):
                data_arrays.extend(model.data_vars.values())
            elif isinstance(model, xr.DataArray):
                data_arrays.append(model)
            else:
                raise TypeError(f"Unsupported type in 'models' list: {type(model)}")
        
        if not data_arrays:
            raise NoDataError("No valid data found in 'models'. Ensure it contains xarray.DataArray or xarray.Dataset objects.")

        self.models = data_arrays






        

        



        





