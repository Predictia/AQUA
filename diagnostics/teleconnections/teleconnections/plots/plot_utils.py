import math


def plot_box(num_plots=0):
    """
    Evaluate the number of rows and columns for a plot
    based on the number of plots to be plotted.

    Args:
        num_plots (int): Number of plots to be plotted.

    Returns:
        num_rows (int): Number of rows for the plot.
        num_cols (int): Number of columns for the plot.

    Raises:
        ValueError: If the number of plots is 0.
    """
    if num_plots == 0:
        raise ValueError('Number of plots must be greater than 0.')

    num_cols = math.ceil(math.sqrt(num_plots))
    num_rows = math.ceil(num_plots / num_cols)

    return num_rows, num_cols


def minmax_maps(maps=None):
    """
    Find the minimum and maximum values of the maps values
    for a list of maps.

    Args:
        regs (list): List of maps.

    Returns:
        vmin (float): Minimum value of the maps.
        vmax (float): Maximum value of the maps.
    """

    minmax = (min([map.values.min() for map in maps]),
              max([map.values.max() for map in maps]))
    vmin = minmax[0]
    vmax = minmax[1]

    return vmin, vmax


def set_layout(ax, title=None, xlabel=None, ylabel=None, xlog=False,
               ylog=False, xlim=None, ylim=None):
    """
    Set the layout of the plot

    Args:
        ax (Axes):              Axes object
        title (str,opt):        title of the plot
        xlabel (str,opt):       label of the x axis
        ylabel (str,opt):       label of the y axis
        xlog (bool,opt):        enable or disable x axis log scale,
                                default is False
        ylog (bool,opt):        enable or disable y axis log scale,
                                default is False
        xlim (tuple,opt):       x axis limits
        ylim (tuple,opt):       y axis limits

    Returns:
        fig (Figure):           Figure object
        ax (Axes):              Axes object
    """
    if title:
        ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if xlog:
        ax.set_xscale('symlog')
    if ylog:
        ax.set_yscale('symlog')
    if xlim:
        ax.set_xlim(xlim)
    if ylim:
        ax.set_ylim(ylim)

    return ax
