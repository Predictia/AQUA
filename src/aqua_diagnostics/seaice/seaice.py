""" Seaice doc """
import os
import xarray as xr

from aqua.diagnostics.core import Diagnostic
from aqua.exceptions import NoDataError, NotEnoughDataError
from aqua.logger import log_configure
from aqua.reader import Reader, inspect_catalog
from aqua.util import ConfigPath, OutputSaver
from aqua.util import load_yaml

xr.set_options(keep_attrs=True)

class SeaIce(Diagnostic):
    """Class for teleconnection objects."""

    def __init__(self, model: str, exp: str, source: str,        
                 catalog=None,
                 regrid=None, 
                 regionfile=load_yaml(),
                 loglevel: str = 'WARNING'
                 ):

        super().__init__(model=model, exp=exp, source=source,
                         regrid=regrid, catalog=catalog, loglevel=loglevel)
        
        folderpath = ConfigPath().get_config_dir()
        

        if regionfile is None:
            regionfile = load_yaml(infile=)

#threshold=0.15 in eval extent