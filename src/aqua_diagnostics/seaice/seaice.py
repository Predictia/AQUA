""" Seaice doc """
import os
import xarray as xr

from aqua.diagnostics.core import Diagnostic
from aqua.exceptions import NoDataError, NotEnoughDataError
from aqua.logger import log_configure
from aqua.util import ConfigPath, OutputSaver
from aqua.util import load_yaml, area_selection, to_list

xr.set_options(keep_attrs=True)

class SeaIce(Diagnostic):
    """Class for seaice objects."""

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

        # load the region file
        self.regions_definition = load_yaml(infile=regions_file)

        if regions is None:
            self.logger.warning('No regions defined. Using all available regions.')
            self.regions = list(self.regions_definition.keys())
        else:
            # if only one region is given as a string, it is converted to a list of strings with only one element
            # to avoid characters splitting. If the region is not in the regions_definition file, it will be added to the invalid_regions list.
            invalid_regions = [reg for reg in to_list(regions) if reg not in self.regions_definition.keys()]

            # If invalid regions are found, raise an error and list them
            if invalid_regions:
                raise ValueError(f"Invalid region name(s): [{', '.join(f'{i}' for i in invalid_regions)}]. Please check the region file at: f'{regions_file}'.")
            
            self.regions = to_list(regions)
        
        self.extent = None

    def show_regions(self):
        """Show the regions available in the region file."""

        return dict(self.regions_definition)

    def _compute_extent(self, threshold=0.15, var='siconc'):
        """Compute sea ice extent.
        threshold (float): The threshold value for which sea ice fraction is considered . Default is 0.15.
        """

        # retrieve data with Diagnostic method
        super().retrieve(var=var)

        # get the sea ice concentration mask
        ci_mask = self.data[var].where((self.data[var] > threshold) &
                                       (self.data[var] < 1.0))
        
        # make a list to store the extent DataArrays for each region
        extent = []
        for region in self.regions:
            self.logger.info(f'Computing sea ice extent for {region}')
            box = self.regions_definition[region]

            # get info on grid area that must be reinitialised for each region
            areacello = self.reader.grid_area

            # regional selection
            areacello = area_selection(areacello, lat=[box["latS"], box["latN"]], lon=[box["lonW"], box["lonE"]],
                                       loglevel=self.loglevel)

            # compute sea ice extent: exclude areas with no sea ice and sum over the spatial dimension, divide by 1e12 to convert to million km^2
            seaice_extent = areacello.where(ci_mask.notnull()).sum(skipna = True, min_count = 1, dim=self.reader.space_coord) / 1e12
            
            # add/fix attributes
            seaice_extent.attrs["units"] = "million km^2"
            seaice_extent.attrs["long_name"] = f"Sea ice extent integrated over {region} region"
            seaice_extent.attrs["standard_name"] = f"{region} sea ice extent"
            seaice_extent.attrs["region"] = region
            seaice_extent.name = f"sea_ice_extent_{region.replace(' ', '_').lower()}"

            extent.append(seaice_extent)
        
        # combine the extent DataArrays into a single Dataset and keep as global attributes 
        # only the attrs that are shared across all DataArrays
        self.extent = xr.merge(extent, combine_attrs='drop_conflicts')
       
        return self.extent

    def _compute_volume(self, var='sithick'):
        """Compute sea ice volume."""

        # retrieve data with Diagnostic method
        super().retrieve(var=var)

        if self.data is None:
            self.logger.error(f"Variable {var} not found in dataset {self.model}, {self.exp}, {self.source}")
            raise NoDataError("Variable not found in dataset")

        # get the sea ice volume
        sivol_mask = self.data[var].where((self.data[var] > 0) &
                                          (self.data[var] < 99.0))

        # make a list to store the volume DataArrays for each region
        volume = []
        for region in self.regions:

            # get info on grid area that must be reinitialised for each region
            areacello = self.reader.grid_area

            self.logger.info(f'Computing sea ice volume for {region}')
            box = self.regions_definition[region]

            # regional selection
            areacello = area_selection(areacello, lat=[box["latS"], box["latN"]], lon=[box["lonW"], box["lonE"]], 
                                       loglevel=self.loglevel)

            # compute sea ice volume: exclude areas with no sea ice and sum over the spatial dimension, divide by 1e12 to convert to km^3
            seaice_volume = (sivol_mask * areacello.where(sivol_mask.notnull())).sum(skipna = True, min_count = 1, 
                                                                                     dim=self.reader.space_coord) / 1e12
            # add/fix attributes
            seaice_volume.attrs["units"] = "km^3"
            seaice_volume.attrs["long_name"] = f"Sea ice volume integrated over {region} region"
            seaice_volume.attrs["standard_name"] = f"{region} sea ice volume"
            seaice_volume.attrs["region"] = region
            seaice_volume.name = f"sea_ice_volume_{region.replace(' ', '_').lower()}"

            volume.append(seaice_volume)

        # combine the volume DataArrays into a single Dataset and keep as global attributes 
        # only the attrs that are shared across all DataArrays
        self.volume = xr.merge(volume, combine_attrs='drop_conflicts')
       
        return volume

    def compute_seaice(self, method, *args, **kwargs):
        """ Execute the seaice diagnostic based on the specified method.

        Parameters:
        var (str): The variable to be used for computation. Default is None.
        method (str): The method to compute sea ice metrics. Options are 'extent' or 'volume'. Default is 'extent'.
        Kwargs:
            - threshold (float): The threshold value for which sea ice fraction is considered. Default is 0.15.
            - var (str): The variable to be used for computation. Default is 'sithick'.
        Returns:
        xr.DataArray or xr.Dataset: The computed sea ice metric. A Dataset is returned if multiple regions are requested.
        
        Raises:
        ValueError: If an invalid method is specified.
        """

        # create a dictionary with the available methods associated with the corresponding function
        methods = {
            'extent': self._compute_extent,
            'volume': self._compute_volume,
            }

        # check if the method is valid and call the corresponding function if so
        if method not in methods:
                valid_methods = ', '.join(f"'{key}'" for key in methods.keys())
                raise ValueError(f"Invalid method '{method}'. Please choose from: [ {valid_methods} ]")
        else:
            # call the function associated with the method
            return methods[method](*args, **kwargs)
