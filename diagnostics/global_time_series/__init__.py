from .gregory import plot_gregory
from .timeseries import Timeseries

__version__ = "0.0.5"

__all__ = ["plot_gregory",
           "Timeseries"]

# Changelog:

# 0.0.5: support for reference data in Gregory plot
# 0.0.4: gregory plot in a separate file
# 0.0.3: added improvement gregory plot
#        obs dataset errorbar
# 0.0.2: added CLI for workflow
# 0.0.1: initial release
