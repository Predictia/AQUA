"""tropical_cyclones plotting module"""

from .plotting_TCs import multi_plot, plot_trajectories

# Optional but recommended
__version__ = '0.2.0'

# This specifies which methods are exported publicly, used by "from tropical cyclones import *"
__all__ = ["multi_plot", "plot_trajectories"]
