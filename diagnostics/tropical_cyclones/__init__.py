"""tropical_cyclones module"""

# The following lines are needed so that the tropical cyclones class constructor
# and associated functions are available directly from the module "tropical_cyclones"


from .dummy_class_readerwrapper import DummyDiagnosticWrapper
from .dummy_class_timeband import DummyDiagnostic
from .dummy_func import dummy_func

# Optional but recommended
__version__ = '0.0.1'

# This specifies which methods are exported publicly, used by "from dummy import *"
__all__ = ["DummyDiagnostic", "DummyDiagnosticWrapper", "dummy_func"]
