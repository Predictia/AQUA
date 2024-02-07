"""AQUA module"""
import warnings
from .docker import rundiag
from .graphics import plot_single_map
from .gribber import Gribber
from .lra_generator import LRAgenerator
from .reader import Reader, catalogue, Streaming, inspect_catalogue
from .slurm import squeue, job, output_dir, scancel, max_resources_per_node
from .accessor import AquaAccessor

# Warning settings can be changed here
# warnings.filterwarnings("all", category=DeprecationWarning)

__version__ = '0.6.3'

__all__ = ["rundiag",
           "plot_single_map",
           "Gribber",
           "LRAgenerator",
           "Reader", "catalogue", "Streaming", "inspect_catalogue",
           "squeue", "job", "output_dir", "scancel", "max_resources_per_node"]
