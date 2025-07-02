import xarray as xr
import matplotlib.pyplot as plt

from aqua.logger import log_configure
from .styles import ConfigStyle
from .lat_lon_profiles import plot_lat_lon_profiles
    
def plot_multi_lines(data_arrays_list,
                     data_labels: list = None,
                     style: str = None,
                     loglevel='WARNING',
                     title: str = None,
                     **kwargs):
    """
    Plot multiple data arrays on the same plot for comparison.
    
    Args:
        data_arrays_list (list): List of data arrays to plot
        data_labels (list): Labels for each data array
        style (str): Style for the plot
        loglevel (str): Logging level
        title (str): Plot title
        **kwargs: Additional plotting arguments
    
    Returns:
        fig, ax: Matplotlib figure and axes objects
    """
    
    logger = log_configure(loglevel, 'plot_multi_lines')
    ConfigStyle(style=style, loglevel=loglevel)
    
    fig, ax = plt.subplots(figsize=kwargs.get('figsize', (10, 6)))
    
    for i, data in enumerate(data_arrays_list):
        label = data_labels[i] if data_labels and i < len(data_labels) else f"Data {i+1}"
        plot_lat_lon_profiles(monthly_data=data, 
                              data_labels=[label],
                              fig=fig, ax=ax)
    
    if title:
        ax.set_title(title, fontsize=13, fontweight='bold')
    
    ax.legend(fontsize='small')
    ax.grid(True, linestyle='--', alpha=0.7)
    
    return fig, ax