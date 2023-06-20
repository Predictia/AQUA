"""teleconnections module"""
from .cdo_testing import station_based_cdo, regional_mean_cdo, regional_anomalies_cdo
from .index import station_based_index, regional_mean_index, regional_mean_anomalies
from .plots import cor_plot, reg_plot, simple_plot, index_plot
from .tools import load_namelist, lon_180_to_360

__version__ = '0.0.2'
