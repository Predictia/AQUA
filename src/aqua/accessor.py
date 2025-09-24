"Module defining a new aqua accessor to extend xarray"

import xarray as xr
import aqua


# For now not distinguishing between dataarray and dataset methods
@xr.register_dataset_accessor("aqua")
@xr.register_dataarray_accessor("aqua")
class AquaAccessor:

    def __init__(self, xarray_obj):
        self._obj = xarray_obj
        self.instance = aqua.Reader.instance  # by default use the latest available instance of the Reader class

    def set_default(self, reader):
        """
        Sets a specific reader instance as default for further accessor uses.
        Arguments:
            reader (object of class Reader): the reader to set as default

        Returns:
            None
        """
        reader.set_default()  # set this also as the next Reader default
        self.instance = reader  # set as reader to be used for the accessor
        return self._obj

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
        """Perform time averaging."""
        return self.instance.timmean(self._obj, **kwargs)
    
    def timmax(self, **kwargs):
        """Perform time maximum."""
        return self.instance.timmax(self._obj, **kwargs)
    
    def timmin(self, **kwargs):
        """Perform time minimum."""
        return self.instance.timmin(self._obj, **kwargs)
    
    def timstd(self, **kwargs):
        """Perform time standard deviation."""
        return self.instance.timstd(self._obj, **kwargs)
    
    def timstat(self, **kwargs):
        """Perform time statistics."""
        return self.instance.timstat(self._obj, **kwargs)

    def fldmean(self, **kwargs):
        """Perform a weighted global average."""
        return self.instance.fldmean(self._obj, **kwargs)

    def vertinterp(self, **kwargs):
        """A basic vertical interpolation."""
        return self.instance.vertinterp(self._obj, **kwargs)

    def detrend(self, **kwargs):
        """A basic detrending."""
        return self.instance.detrend(self._obj, **kwargs)

    def stream(self, **kwargs):
        """Stream the dataset."""
        return self.instance.stream(self._obj, **kwargs)

    def histogram(self, **kwargs):
        """Compute a histogram (or pdf) of the data."""
        return self.instance.histogram(self._obj, **kwargs)
