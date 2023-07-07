"""teleconnections module"""
from .cdo_testing import station_based_cdo, regional_mean_cdo
from .cdo_testing import regional_anomalies_cdo
from .index import station_based_index, regional_mean_index
from .index import regional_mean_anomalies
from .plots import minmax_maps, plot_box, index_plot, maps_plot
from .plots import single_map_plot
from .statistics import reg_evaluation, cor_evaluation
from .tc_class import Teleconnection
from .tools import load_namelist, lon_180_to_360, lon_360_to_180
from .tools import area_selection, wgt_area_mean
from .tools import get_dataset_config

__version__ = '0.0.7'

__all__ = ['station_based_cdo', 'regional_mean_cdo', 'regional_anomalies_cdo',
           'station_based_index', 'regional_mean_index',
           'regional_mean_anomalies',
           'minmax_maps', 'plot_box', 'index_plot', 'maps_plot',
           'single_map_plot',
           'reg_evaluation', 'cor_evaluation',
           'Teleconnection', 'load_namelist', 'lon_180_to_360',
           'lon_360_to_180', 'area_selection',
           'wgt_area_mean', 'get_dataset_config']

# Change log
# 0.0.7: CLI refined, get_dataset_config moved to tools, tools refactor
# 0.0.6: plots submodules added
# 0.0.5: comparison_index_plot, cli for single and multiple datasets added
# 0.0.4: Added cor_evaluation and reg_evaluation based on sacpy,
#        removed deprecated functions
# 0.0.3: Class Teleconnection added
# 0.0.2: Added package version
# 0.0.1: Initial version
