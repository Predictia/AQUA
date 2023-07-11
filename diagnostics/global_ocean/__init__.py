
"""Global Ocean module""" 


from .global_ocean import *

# Optional but recommended
__version__ = '0.0.1'

# This specifies which methods are exported publicly, used by "from dummy import *"
__all__ = ["hovmoller_plot", "time_series", "multilevel_t_s_trend_plot", "zonal_mean_trend_plot"]

