import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from aqua.logger import log_configure
from .styles import ConfigStyle
import re


def normalize_unit_string(unit):
    """
    Normalize unit strings to a consistent format.
    Args:
        unit (str): The unit string to normalize.
    Returns:
        str: Normalized unit string.
    """
    if not unit:
        return None
    # Remove leading and trailing whitespace, and replace '**' with '^'
    unit = unit.replace(' ', '').replace('**', '^')
    # Handle common unit formats
    unit = re.sub(r'm-2', 'm^-2', unit)
    unit = re.sub(r'm\^\(-?2\)', 'm^-2', unit)
    
    if unit in ['Wm^-2', 'W/m^2', 'W/m^-2']:
        unit = 'W/m²'

    return unit

def boxplot(fldmeans, model_names, variables, variable_names=None, title=None, style=None, loglevel='WARNING'):
    """
    Generate a boxplot of precomputed field-mean values for multiple variables and models.

    Args:
        fldmeans (list of xarray.Dataset): Precomputed fldmean() for each model.
        model_names (list of str): Names corresponding to each fldmean dataset.
        variables (list of str): Variable names to be plotted (as in the fldmean Datasets).
        variable_names (list of str, optional): Display names for the variables.
        title (str, optional): Title for the plot.
        style (str, optional): Style to apply to the plot.
        loglevel (str): Logging level, unused but kept for compatibility.

    Returns:
        tuple: Matplotlib figure and axis.
    """

    logger = log_configure(loglevel, 'boxplot')
    ConfigStyle(style=style, loglevel=loglevel)
    
    sns.set_palette("pastel")
    fontsize = 18

    # Map internal variable names to display names
    label_map = {
        var_name: name for var_name, name in zip(variables, variable_names)
    } if variable_names and len(variable_names) == len(variables) else {var: var for var in variables}

    # check units consistency
    unit_map = {}  
    global_units_found = set()

    for var_name in variables:
        var = var_name[1:] if var_name.startswith('-') else var_name
        units_for_var = set()

        for model_ds in fldmeans:
            unit = normalize_unit_string(model_ds[var].attrs.get('units')) if var in model_ds else None
            if unit:
                units_for_var.add(unit)
            else:
                logger.warning(f"No units found for variable '{var}' in a dataset")

        unit_map[var_name] = units_for_var
        if len(units_for_var) > 1:
            logger.warning(f"Inconsistent units for variable '{var}': {units_for_var}")

    # Collect data
    boxplot_data = {'Variables': [], 'Values': [], 'Datasets': []}
    for model_ds, model_name in zip(fldmeans, model_names):
        for var_name in variables:
            var = var_name[1:] if var_name.startswith('-') else var_name  # Remove leading '-' if present
            if var not in model_ds:
                continue
            values = model_ds[var].values.flatten()
            if var_name.startswith('-'):
                values = -values
            values = values[np.isfinite(values)]
            boxplot_data['Variables'].extend([label_map[var_name]] * len(values))
            boxplot_data['Values'].extend(values)
            boxplot_data['Datasets'].extend([model_name] * len(values))

    # Build DataFrame
    df = pd.DataFrame(boxplot_data)

    # Plot
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.boxplot(data=df, x='Variables', y='Values', hue='Datasets', ax=ax)

    if title:
        ax.set_title(title, fontsize=fontsize + 4)

    ax.set_xlabel('Variables', fontsize=fontsize)

    # Determine y-axis label based on units
    global_units_found = set().union(*unit_map.values())
    if len(global_units_found) == 1:
        ax.set_ylabel(next(iter(global_units_found)), fontsize=fontsize, labelpad=12)    
    else:
        ax.set_ylabel('Values (various units)', fontsize=fontsize, labelpad=12)

    ax.tick_params(axis='x', labelsize=fontsize - 4)
    ax.tick_params(axis='y', labelsize=fontsize - 4)
    ax.legend(loc='upper right', fontsize=fontsize)
    ax.grid(True)
    fig.tight_layout()

    return fig, ax