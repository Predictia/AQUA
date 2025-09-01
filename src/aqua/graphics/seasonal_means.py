import xarray as xr
import matplotlib.pyplot as plt

from .styles import ConfigStyle
from .lat_lon_profiles import plot_lat_lon_profiles

def plot_seasonal_lat_lon_profiles(seasonal_data,
                                   ref_data=None,
                                   std_data=None,
                                   ref_std_data=None,
                                   style: str = None,
                                   loglevel='WARNING',
                                   data_labels: list = None,
                                   title: str = None,
                                   ):
    """
   Plot seasonal lat-lon profiles in a 2x2 subplot layout for the four meteorological seasons.

    This function creates exactly 4 subplots arranged in a 2x2 grid, each showing lat-lon 
    profiles for a specific season. The seasons are hardcoded and must be provided in the 
    exact order: [DJF, MAM, JJA, SON].

    Args:
        seasonal_data (list): List of exactly 4 elements, one for each season.
            Must be in order: [DJF, MAM, JJA, SON].
            Each element can be either:
            - A single xarray DataArray (for single model)
            - A list of xarray DataArrays (for multiple models)
            
            Examples:
            Single model: [djf_data, mam_data, jja_data, son_data]
            Multiple models: [[model1_djf, model2_djf], [model1_mam, model2_mam], ...]
            
            DJF = December-January-February (Winter)
            MAM = March-April-May (Spring) 
            JJA = June-July-August (Summer)
            SON = September-October-November (Autumn)
        ref_data (list, optional): Reference data for each season, same structure as seasonal_data.
        std_data (list, optional): Standard deviation data for each season, same structure as seasonal_data.
        ref_std_data (list, optional): Reference standard deviation data for each season.
        style (str, optional): Style configuration for the plot.
        loglevel (str): Logging level.
        data_labels (list, optional): Labels for the data series.
        title (str, optional): Overall title for the 2x2 subplot figure.

    Returns:
        fig, axs: Matplotlib figure and axes objects (2x2 subplot layout).
        
    Raises:
        ValueError: If seasonal_data is not a list of exactly 4 elements.
    """
    ConfigStyle(style=style, loglevel=loglevel)
    
    # Validate input data structure - now only 4 seasons
    if not isinstance(seasonal_data, list) or len(seasonal_data) != 4:
        raise ValueError("seasonal_data must be a list of 4 elements: [DJF, MAM, JJA, SON]")
    
    # Validate std_data if provided
    if std_data is not None:
        computed_std_data = []
        for s in std_data:
            if s is not None and hasattr(s, 'compute'):
                computed_std_data.append(s.compute())
            else:
                computed_std_data.append(s)
        std_data = computed_std_data
    else:
        std_data = [None] * 4

    # Validate ref_std_data if provided
    if ref_std_data is not None:
        computed_ref_std_data = []
        for s in ref_std_data:
            if s is not None and hasattr(s, 'compute'):
                computed_ref_std_data.append(s.compute())
            else:
                computed_ref_std_data.append(s)
        ref_std_data = computed_ref_std_data
    else:
        ref_std_data = [None]

    fig, axs = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    axs = axs.flatten()
    season_names = ["DJF", "MAM", "JJA", "SON"]

    # Plot the 4 seasonal subplots
    for i, ax in enumerate(axs):
        season_data = seasonal_data[i]
        season_ref_data = ref_data[i] if ref_data is not None and i < len(ref_data) else None
        season_std_data = std_data[i] if std_data is not None and i < len(std_data) else None
        season_ref_std_data = ref_std_data[i] if ref_std_data is not None and i < len(ref_std_data) else None
        
        if season_ref_data is not None:
            ref_label = f"{season_ref_data.attrs.get('AQUA_model', 'Reference')} {season_ref_data.attrs.get('AQUA_exp', 'Data')}"
            
            if isinstance(season_data, list):
                # Handle multiple model data
                model_labels = []
                for j, data in enumerate(season_data):
                    if data_labels and j < len(data_labels):
                        label = data_labels[j]
                    else:
                        model = data.attrs.get('AQUA_model', f'Model {j+1}')
                        exp = data.attrs.get('AQUA_exp', '')
                        label = f"{model} {exp}".strip()
                    model_labels.append(label)
                
                _, _ = plot_lat_lon_profiles(data=season_data,
                                    ref_data=season_ref_data,
                                    std_data=season_std_data,
                                    ref_std_data=season_ref_std_data,
                                    data_labels=model_labels,
                                    ref_label=ref_label,
                                    fig=fig, ax=ax,
                                    loglevel=loglevel)
            else:
                # Single model data
                model_label = data_labels[0] if data_labels and len(data_labels) > 0 else f"{season_data.attrs.get('AQUA_model', 'Model')} {season_data.attrs.get('AQUA_exp', 'Exp')}"
                
                _, _ = plot_lat_lon_profiles(data=[season_data],
                                    ref_data=season_ref_data,
                                    std_data=season_std_data,
                                    ref_std_data=season_ref_std_data,
                                    data_labels=[model_label],
                                    ref_label=ref_label,
                                    fig=fig, ax=ax,
                                    loglevel=loglevel)
        else:
            # No reference data, just plot model data
            _, _ = plot_lat_lon_profiles(data=season_data,
                                std_data=season_std_data,
                                ref_std_data=season_ref_std_data,
                                data_labels=data_labels,
                                fig=fig, ax=ax,
                                loglevel=loglevel)
        
        ax.set_title(season_names[i])
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Show legend only on the first subplot
        if i == 0:
            ax.legend(fontsize='small', loc='upper right')
        elif hasattr(ax, 'legend_') and ax.legend_:
            ax.legend_.remove()
    
    # Add overall title if provided
    if title:
        fig.suptitle(title, fontsize=14, fontweight='bold', y=0.98)
    
    return fig, axs
    