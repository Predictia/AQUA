"""ssh module"""

#To enable: from ssh import class sshVariability

from .ssh_variability import sshVariabilityCompute
from .plot_ssh_variability import sshVariabilityPlot

# This specifies which methods are exported publicly, used by "from ssh_class *"
__all__ = ["sshVariabilityCompute", "sshVariablityPlot"]
