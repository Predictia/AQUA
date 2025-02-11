""" Seaice doc """
import os
import xarray as xr

from aqua.diagnostics.core import Diagnostic
from aqua.exceptions import NoDataError, NotEnoughDataError
from aqua.logger import log_configure
from aqua.util import ConfigPath, OutputSaver
from aqua.util import load_yaml, area_selection

xr.set_options(keep_attrs=True)

class SeaIce(Diagnostic):
    """Class for teleconnection objects."""

    def __init__(self, model: str, exp: str, source: str,        
                 catalog=None,
                 regrid=None, 
                 startdate=None, enddate=None,
                 regions=['Arctic', 'Antarctic'],
                 regions_file=None,
                 loglevel: str = 'WARNING'
                 ):

        super().__init__(model=model, exp=exp, source=source,
                         regrid=regrid, catalog=catalog, 
                         startdate=startdate, enddate=enddate,
                         loglevel=loglevel)
        self.logger = log_configure(loglevel, 'SeaIce')
        
        # region file is the fullpath to the region file
        if regions_file is None:
            folderpath = ConfigPath().get_config_dir()
            regions_file = os.path.join(folderpath, 'diagnostics', 'seaice', 'config', 'regions_definition.yaml')
        
        self.regions_definition = load_yaml(infile=regions_file)

        if regions is None:
            self.logger.warning('No regions defined. Using all available regions.')
            self.regions = list(self.regions_definition.keys())
        else:
            if not all(reg in self.regions_definition.keys() for reg in regions):
                raise ValueError('Invalid region name. Please check the region file.')
            self.regions = regions

        # create an empty dictionary to store the extent of each region
        self.extent = {region: None for region in self.regions}

    def show_regions(self):
        """Show the regions available in the region file."""

        return dict(self.regions_definition)
            
    def compute_extent(self, threshold=0.15, var='siconc'):
        """Compute sea ice extent."""
        
        # retrieve data with Diagnostic method
        super().retrieve(var=var)

        # get the sea ice concentration mask
        ci_mask = self.data[var].where((self.data[var] > threshold) &
                                          (self.data[var] < 1.0))
        
        # get info on grid area
        areacello = self.reader.grid_area

        for region in self.regions:
            self.logger.info(f'Computing sea ice extent for {region}')
            box = self.regions_definition[region]

            # regional selection
            areacello = area_selection(areacello, lat=[box["latS"], box["latN"]], lon=[box["lonW"], box["lonE"]])

            # compute sea ice extent: exclude areas with no sea ice and sum over the spatial dimension, divide by 1e12 to convert to million km^2
            seaice_extent = areacello.where(ci_mask.notnull()).sum(skipna = True, min_count = 1, dim=self.reader.space_coord) / 1e12
            
            # add/fix attributes
            seaice_extent.attrs["units"] = "million km^2"
            seaice_extent.attrs["long_name"] = "Sea ice extent"
            seaice_extent.attrs["standard_name"] = "extent"
            seaice_extent.attrs["region"] = region
            seaice_extent.name = "sea_ice_extent"

            self.extent[region] = seaice_extent
       
        return self.extent