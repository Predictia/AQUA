"Module defining a new aqua accessor to extend xarray"

import aqua
import xarray as xr

# For now not distinguishing between dataarray and dataset methods
@xr.register_dataset_accessor("aqua")
@xr.register_dataarray_accessor("aqua")
class AquaAccessor:
    def __init__(self, xarray_obj):
        self._obj = xarray_obj

    def plot_single_map(self, **kwargs):
        """Plot contour or pcolormesh map of a single variable."""
        aqua.graphics.plot_single_map(self._obj, **kwargs)

    def area_selection(self, **kwargs):
        """Extract a custom area from a DataArray."""
        return aqua.util.area_selection(self._obj, **kwargs)

# @xr.register_dataset_accessor("aqua")
# class AquaAccessorDS:
#     def __init__(self, xarray_obj):
#         self._obj = xarray_obj



