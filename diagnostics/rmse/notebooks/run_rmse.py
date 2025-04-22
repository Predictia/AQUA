import sys
from importlib import reload

sys.path.append('/gpfs/projects/ehpc165/evaluation_framework/AQUA/diagnostics/rmse')
from rmse import RMSE

config = '/gpfs/projects/ehpc165/evaluation_framework/AQUA/diagnostics/rmse/config/config.yaml'
diagnostic = RMSE(config=config)
diagnostic.retrieve()
diagnostic.spatial_rmse(save_fig=True, save_netcdf=True)
diagnostic.temporal_rmse(save_fig=True, save_netcdf=True)