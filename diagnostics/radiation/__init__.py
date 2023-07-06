"""radiation module"""

from .functions import radiation_diag

# Optional but recommended
__version__ = '0.0.1'

# This specifies which methods are exported publicly, used by "from dummy import *"
__all__ = ["process_ceres_data", "process_model_data", "process_era5_data", "process_ceres_sfc_data", "gregory_plot", "barplot_model_data", "plot_model_comparison_timeseries", "plot_bias", "plot_maps"]