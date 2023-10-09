"""radiation module"""

from .functions import process_ceres_data, process_model_data, process_era5_data, process_ceres_sfc_data
from .functions import gregory_plot, barplot_model_data, plot_model_comparison_timeseries, plot_bias, plot_maps, plot_mean_bias
from .radiation_functions import new_process_ceres_data,  new_process_model_data, new_barplot_model_data


# Optional but recommended
__version__ = '0.0.1'

# This specifies which methods are exported publicly, used by "from radiation import *"
__all__ = ["new_process_ceres_data", "new_process_model_data", "process_ceres_data", "process_model_data", "process_era5_data", "process_ceres_sfc_data", "gregory_plot", 
           "barplot_model_data", "new_barplot_model_data", "plot_model_comparison_timeseries", "plot_bias", "plot_maps", "plot_mean_bias"]