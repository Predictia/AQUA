"""AQUA module"""
from .version import __version__
from .graphics import plot_single_map, plot_maps, plot_single_map_diff, plot_timeseries
from .graphics import plot_hovmoller
from .lra_generator import LRAgenerator
from .reader import Reader, catalog, Streaming, inspect_catalog
from. regridder import Regridder
from .slurm import squeue, job, output_dir, scancel, max_resources_per_node
from .accessor import AquaAccessor

__all__ = ["plot_single_map", "plot_maps", "plot_single_map_diff", "plot_timeseries",
           "plot_hovmoller",
           "LRAgenerator",
           "Reader", "catalog", "Streaming", "inspect_catalog",
           "Regridder",
           "squeue", "job", "output_dir", "scancel", "max_resources_per_node"]
