import xarray as xr
import matplotlib.pyplot as plt

from aqua.logger import log_configure
from aqua.util import to_list
from .util_timeseries import plot_timeseries_data
from .styles import ConfigStyle

def plot_lat_lon_profiles(data: xr.DataArray = None,
                          data_labels: list = None,
                          data_type: str = 'auto',  # 'monthly', 'annual', or 'auto'
                          style: str = None,
                          fig: plt.Figure = None, 
                          ax: plt.Axes = None,
                          loglevel='WARNING',
                          **kwargs):
    """
    Plot latitude or longitude profiles of data, averaging over the specified axis.

    Args:
        data (xr.DataArray or list): Data to plot.
        data_labels (list, optional): Labels for the data.
        data_type (str, optional): Type of data for styling ('monthly', 'annual', or 'auto').
                                  If 'auto', tries to infer from data attributes.
        style (str, optional): Style for the plot.
        fig (plt.Figure, optional): Matplotlib figure object.
        ax (plt.Axes, optional): Matplotlib axes object.
        loglevel (str, optional): Logging level.
        **kwargs: Additional keyword arguments for customization.

    Returns:
        tuple: Matplotlib figure and axes objects.
    """

    logger = log_configure(loglevel, 'plot_lat_lon_profiles')
    ConfigStyle(style=style, loglevel=loglevel)

    # Convert inputs to lists
    data_list = to_list(data)
    labels_list = to_list(data_labels)

    if not data_list:
        raise ValueError("No data provided for plotting")

    # Infer data type if set to 'auto'
    if data_type == 'auto':
        # Try to infer from time frequency in the data
        first_data = data_list[0]
        if hasattr(first_data, 'time') and len(first_data.time) > 1:
            time_diff = (first_data.time[1] - first_data.time[0]).values
            # Rough heuristic: if time difference is around 30 days, it's monthly
            if 25 <= time_diff.astype('timedelta64[D]').astype(int) <= 35:
                data_type = 'monthly'
            elif time_diff.astype('timedelta64[D]').astype(int) >= 300:
                data_type = 'annual'
            else:
                data_type = 'monthly'  # default
        else:
            data_type = 'monthly'  # default

    if fig is None and ax is None:
        fig_size = kwargs.get('figsize', (10, 5))
        fig, ax = plt.subplots(1, 1, figsize=fig_size)

    logger.debug(f"Plotting {len(data_list)} data arrays with data_type: {data_type}")

    # prepare labels if not provided
    if not labels_list or len(labels_list) < len(data_list):
        labels_list = [
            (d.attrs.get("long_name", f"Data {i+1}")) for i, d in enumerate(data_list)
        ]

    plot_timeseries_data(
        ax=ax,
        data=data_list,
        data_labels=labels_list,
        lw=3,
        kind=data_type
    )

    ax.legend(fontsize='small')
    ax.grid(True, axis="y", linestyle='-', color='silver', alpha=0.8)

    title = kwargs.get('title', None)
    if title:
        ax.set_title(title, fontsize=13, fontweight='bold')

    return fig, ax