"""Ocean Circulation module""" 

from .ocean_util import *
from .ocean_circulation import *
from .global_ocean import *

# Optional but recommended
__version__ = '0.0.1'

# This specifies which methods are exported publicly, used by "from dummy import *"
__all__ = ["plot_spatial_mld_clim", "plot_stratification"]