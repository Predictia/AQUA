"""
Module for plotting teleconnection indices and maps.
A function for Hovmoller plot is added.
"""
from .index_plot import index_plot, indexes_plot
from .maps_plot import maps_diffs_plot

__all__ = ['index_plot', 'indexes_plot',
           'maps_diffs_plot']
