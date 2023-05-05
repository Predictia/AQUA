import sys
import os
import matplotlib.pyplot as plt

from aqua import Reader

#package_dir = os.path.abspath('/home/dese28/dese28422/one_pass')
sys.path.append('/home/b/b382397/diagnostics/one_pass')
sys.path.append(os.path.abspath("/home/b/b382397/diagnostics/gsv_interface/"))
#/home/dese28/dese28422/gsv_interface
# Now you can import your package


import os
import xarray as xr
import dask as dk
import numpy as np
from one_pass.opa import *
from one_pass.opa import Opa
# from gsv import GSVRetriever

# gsv = GSVRetriever()

# file_path = "/home/dese28/dese28422/one_pass/config.yml"

thetao_monthly_mean_dic = {"stat": "mean",
    "stat_freq": "monthly",
    "output_freq": "monthly",
    "time_step": 1440, # timestep of data in minutes
    "variable": "thetao",
    "save": False,
    "checkpoint": False,
    "checkpoint_file": "./",
    "out_filepath": "./"}
thetao_monthly_mean_opa=Opa(thetao_monthly_mean_dic)

so_monthly_mean_dic = {"stat": "mean",
    "stat_freq": "monthly",
    "output_freq": "monthly",
    "time_step": 1440, # timestep of data in minutes
    "variable": "so",
    "save": False,
    "checkpoint": False,
    "checkpoint_file": "./",
    "out_filepath": "./"}
so_monthly_mean_opa=Opa(so_monthly_mean_dic)

yearly_mean_dic = {"stat": "mean",
    "stat_freq": "monthly",
    "output_freq": "monthly",
    "time_step": 1440, # timestep of data in minutes
    "variable": "thetao",
    "save": False,
    "checkpoint": False,
    "checkpoint_file": "./",
    "out_filepath": "./"}
yearly_mean_opa=Opa(yearly_mean_dic)



