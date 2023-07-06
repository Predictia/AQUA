"""tropical_cyclones module"""

# The following lines are needed so that the tropical cyclones class constructor
# and associated functions are available directly from the module "tropical_cyclones"


from .tropical_cyclones import TCs
from .plotting_TCs import multi_plot, plot_trajectories

# Optional but recommended
__version__ = '0.0.1'

# This specifies which methods are exported publicly, used by "from dummy import *"
__all__ = ["TCs", "multi_plot", "plot_trajectories"]
