"Module defining a new aqua accessor to extend xarray"

import aqua
import xarray as xr

# For now not distinguishing between dataarray and dataset methods
@xr.register_dataset_accessor("aqua")
@xr.register_dataarray_accessor("aqua")
class AquaAccessor:

    def __init__(self, xarray_obj):
        self._obj = xarray_obj
        self.instance = None

    def init(self, reader):
        """Record the Reader instance to use."""
        self.instance = reader
    
    def plot_single_map(self, **kwargs):
        """Plot contour or pcolormesh map of a single variable."""
        aqua.graphics.plot_single_map(self._obj, **kwargs)

    def area_selection(self, **kwargs):
        """Extract a custom area from a DataArray."""
        return aqua.util.area_selection(self._obj, **kwargs)

    def regrid(self, **kwargs):
        """Perform regridding of the input dataset."""
        return self.instance.regrid(self._obj, **kwargs)
    
    def timmean(self, **kwargs):
        """Perform daily and monthly averaging."""
        return self.instance.timmean(self._obj, **kwargs)
    
    def fldmean(self, **kwargs):
        """Perform a weighted global average."""
        return self.instance.fldmean(self._obj, **kwargs)
    
    def vertinterp(self, **kwargs):
        """A basic vertical interpolation."""
        return self.instance.vertinterp(self._obj, **kwargs)
    
    def stream(self, **kwargs):
        """Stream the dataset."""
        return self.instance.stream(self._obj, **kwargs)
    
     