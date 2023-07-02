
"""Global Ocean module"""

# The following lines are needed so that the DummyDiagnosticWrapper, DummyDiagnostic constructors
# + the dummy_func function are available directly from the module "dummy"
# so that we can do "from dummy import DummyDiagnostic"

from .global_ocean_class_basin_T_S_means import Global_OceanDiagnostic
from .global_ocean_func import *

# Optional but recommended
__version__ = '0.0.1'

# This specifies which methods are exported publicly, used by "from dummy import *"
__all__ = ["global_ocean_class_basin_T_S_means", "global_ocean_func"]