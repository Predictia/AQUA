from aqua import Reader, catalogue, inspect_catalogue

import xarray as xr

# Dask: parallel computing with Python
from dask.distributed import Client
import dask
dask.config.config.get('distributed').get('dashboard').update({'link':'{JUPYTERHUB_SERVICE_PREFIX}/proxy/{port}/status'})

class 