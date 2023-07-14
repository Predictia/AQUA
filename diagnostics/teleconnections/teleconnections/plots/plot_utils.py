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


def minmax_maps(maps: list):
    """
    Find the minimum and maximum values of the maps values
    for a list of maps.

    After finding the minimum and maximum values,
    values are made simmetric around 0.

    Args:
        regs (list): List of maps.

    Returns:
        vmin (float): Minimum value of the colorbar.
        vmax (float): Maximum value of the colorbar.
    """

    minmax = (min([map.min().values for map in maps]),
              max([map.max().values for map in maps]))

    vmin = minmax[0]
    vmax = minmax[1]

    # Make values simmetric around 0
    absmax = max(abs(vmin), abs(vmax))
    vmin = -absmax
    vmax = absmax

    return vmin, vmax
