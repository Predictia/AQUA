import xarray as xr
import matplotlib.pyplot as plt

from aqua.logger import log_configure
from .styles import ConfigStyle
from .lat_lon_profiles import plot_lat_lon_profiles

def plot_seasonal_and_annual_data(maps,
                                  ref_maps=None,
                                  plot_type: str = 'seasonal',
                                  style: str = None,
                                  loglevel='WARNING',
                                  data_labels: list = None,
                                  title: str = None,
                                  **kwargs):
    
    logger = log_configure(loglevel, 'plot_lines')
    ConfigStyle(style=style, loglevel=loglevel)
    
    # Validate input data structure
    if not isinstance(maps, list) or len(maps) != 5:
        raise ValueError("maps must be a list of 5 elements: [DJF, MAM, JJA, SON, Annual]")
    
    # Create the seasonal plot layout
    if plot_type == 'seasonal':
        fig = plt.figure(figsize=(14, 10), constrained_layout=True)
        gs = fig.add_gridspec(3, 2)
        axs = [
            fig.add_subplot(gs[0, 0]),  # DJF
            fig.add_subplot(gs[0, 1]),  # MAM
            fig.add_subplot(gs[1, 0]),  # JJA
            fig.add_subplot(gs[1, 1]),  # SON
            fig.add_subplot(gs[2, :])   # Annual (big subplot)
        ]
        season_names = ["DJF", "MAM", "JJA", "SON"]
    else:
        raise NotImplementedError("only 'seasonal' plot type is implemented.")

    # ref_maps management
    if ref_maps is not None:
        # model data and reference data are separated
        for i, ax in enumerate(axs[:4]): 
            season_data = maps[i]
            ref_data = ref_maps[i] if i < len(ref_maps) else None
            
            if ref_data is not None:
                ref_label = f"{ref_data.attrs.get('AQUA_model', 'Reference')} {ref_data.attrs.get('AQUA_exp', 'Data')}"
                
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
                    
                    plot_lat_lon_profiles(data=season_data,
                                        ref_data=ref_data,
                                        data_labels=model_labels,
                                        ref_label=ref_label,
                                        fig=fig, ax=ax,
                                        loglevel=loglevel)
                else:
                    # Single model data
                    model_label = data_labels[0] if data_labels and len(data_labels) > 0 else f"{season_data.attrs.get('AQUA_model', 'Model')} {season_data.attrs.get('AQUA_exp', 'Exp')}"
                    
                    plot_lat_lon_profiles(data=[season_data],
                                        ref_data=ref_data,
                                        data_labels=[model_label],
                                        ref_label=ref_label,
                                        fig=fig, ax=ax,
                                        loglevel=loglevel)
            else:
                # no reference data, just plot model data
                plot_lat_lon_profiles(data=season_data,
                                    data_labels=data_labels,
                                    fig=fig, ax=ax,
                                    loglevel=loglevel)
            
            ax.set_title(season_names[i])
            ax.grid(True, linestyle='--', alpha=0.7)
            if i == 0:
                ax.legend(fontsize='x-small', loc='upper right')
            elif hasattr(ax, 'legend_') and ax.legend_:
                ax.legend_.remove()
        
        # annual data (index 4)
        annual_data = maps[4]
        annual_ref = ref_maps[4] if len(ref_maps) > 4 else None

        if annual_ref is not None:
            annual_ref_label = f"{annual_ref.attrs.get('AQUA_model', 'Reference')} {annual_ref.attrs.get('AQUA_exp', 'Data')}"
            
            if isinstance(annual_data, list):
                # Handle multiple model data for annual plot
                annual_labels = []
                for j, data in enumerate(annual_data):
                    if data_labels and j < len(data_labels):
                        label = data_labels[j]
                    else:
                        model = data.attrs.get('AQUA_model', f'Model {j+1}')
                        exp = data.attrs.get('AQUA_exp', '')
                        label = f"{model} {exp}".strip()
                    annual_labels.append(label)
                
                plot_lat_lon_profiles(data=annual_data,
                                    ref_data=annual_ref,
                                    data_labels=annual_labels,
                                    ref_label=annual_ref_label,
                                    fig=fig, ax=axs[4],
                                    loglevel=loglevel)
            else:
                # Single model data for annual plot
                annual_model_label = data_labels[0] if data_labels and len(data_labels) > 0 else f"{annual_data.attrs.get('AQUA_model', 'Model')} {annual_data.attrs.get('AQUA_exp', 'Exp')}"
                
                plot_lat_lon_profiles(data=[annual_data],
                                    ref_data=annual_ref,
                                    data_labels=[annual_model_label],
                                    ref_label=annual_ref_label,
                                    fig=fig, ax=axs[4],
                                    loglevel=loglevel)
        else:
            plot_lat_lon_profiles(data=annual_data,
                                 data_labels=data_labels,
                                 fig=fig, ax=axs[4],
                                 loglevel=loglevel)
        
        axs[4].set_title("Annual Mean")
        axs[4].legend(fontsize='small', loc='upper right')
        axs[4].grid(True, linestyle='--', alpha=0.7)
        
        if title:
            fig.suptitle(title, fontsize=14, fontweight='bold', y=0.98)
        
        return fig, axs
    else:
        # Normal case, no ref_maps provided
        # Plot seasonal means (first 4 panels)
        for i, ax in enumerate(axs[:4]):
            season_data = maps[i]
            
            if len(season_data) == 2:
                # Case: Model data + Reference data nella stessa lista
                model_data = season_data[0]
                ref_data = season_data[1]
                
                # Use provided labels or extract from data attributes
                if data_labels and len(data_labels) >= 2:
                    model_label = data_labels[0]
                    ref_label = data_labels[1]
                else:
                    # Extract from data attributes
                    model_label = f"{model_data.attrs.get('AQUA_model', 'Model')} {model_data.attrs.get('AQUA_exp', 'Exp')}"
                    ref_label = f"{ref_data.attrs.get('AQUA_model', 'Reference')} {ref_data.attrs.get('AQUA_exp', 'Data')}"
                
                # Plot model data and reference data
                plot_lat_lon_profiles(data=model_data,
                                    ref_data=ref_data,
                                    data_labels=[model_label],
                                    ref_label=ref_label,
                                    data_type='auto',
                                    fig=fig, ax=ax,
                                    loglevel=loglevel)
            else:
                # Case: Multiple model data or single data
                labels = []
                for j, data in enumerate(season_data):
                    if data_labels and j < len(data_labels):
                        label = data_labels[j]
                    else:
                        # Extract from data attributes
                        model = data.attrs.get('AQUA_model', f'Data {j+1}')
                        exp = data.attrs.get('AQUA_exp', '')
                        label = f"{model} {exp}".strip()
                    labels.append(label)
                
                plot_lat_lon_profiles(data=season_data,
                                    data_labels=labels,
                                    data_type='auto',
                                    fig=fig, ax=ax,
                                    loglevel=loglevel)
            
            ax.set_title(season_names[i])
            ax.grid(True, linestyle='--', alpha=0.7)
            # Keep the legend only for the first subplot
            if i == 0 and len(season_data) > 1:
                ax.legend(fontsize='x-small', loc='upper right')
            elif hasattr(ax, 'legend_') and ax.legend_:
                ax.legend_.remove()

        # Annual mean (bottom panel)
        annual_data = maps[4]
        
        if len(annual_data) == 2:
            # Case: Model data + Reference data
            model_data = annual_data[0]
            ref_data = annual_data[1]
            
            if data_labels and len(data_labels) >= 2:
                model_label = data_labels[0]
                ref_label = data_labels[1]
            else:
                model_label = f"{model_data.attrs.get('AQUA_model', 'Model')} {model_data.attrs.get('AQUA_exp', 'Exp')}"
                ref_label = f"{ref_data.attrs.get('AQUA_model', 'Reference')} {ref_data.attrs.get('AQUA_exp', 'Data')}"
            
            plot_lat_lon_profiles(data=model_data,
                                ref_data=ref_data,
                                data_labels=[model_label],
                                ref_label=ref_label,
                                data_type='auto',
                                fig=fig,
                                ax=axs[4],
                                loglevel=loglevel)
        else:
            # Case: Multiple model data or single data
            labels = []
            for j, data in enumerate(annual_data):
                if data_labels and j < len(data_labels):
                    label = data_labels[j]
                else:
                    model = data.attrs.get('AQUA_model', f'Data {j+1}')
                    exp = data.attrs.get('AQUA_exp', '')
                    label = f"{model} {exp}".strip()
                labels.append(label)
            
            plot_lat_lon_profiles(data=annual_data,
                                data_labels=labels,
                                data_type='auto',
                                fig=fig,
                                ax=axs[4],
                                loglevel=loglevel)
        
        axs[4].set_title("Annual Mean")
        if len(annual_data) > 1:
            axs[4].legend(fontsize='small', loc='upper right')
        axs[4].grid(True, linestyle='--', alpha=0.7)
        
        # Add overall title if provided
        if title:
            fig.suptitle(title, fontsize=14, fontweight='bold', y=0.98)
        
        return fig, axs
    