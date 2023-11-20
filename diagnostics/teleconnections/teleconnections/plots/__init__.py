"""Module for plotting teleconnection indices and maps."""
from .hovmoller_plot import hovmoller_plot
from .index_plot import index_plot
from .maps_plot import maps_plot, maps_diffs_plot

__all__ = ['hovmoller_plot', 'index_plot',
           'maps_plot', 'maps_diffs_plot']
