import netCDF4 as nc
import timeit
import matplotlib.pyplot as plt
import os 
import re
import json
import cftime 
import xarray as xr
import kerchunk
import kerchunk.hdf
from kerchunk.hdf import SingleHdf5ToZarr
from kerchunk.combine import MultiZarrToZarr

filename = '/work/bb1153/b382075/datasets/MSWEP_V280/Past/Daily/1987121.nc'
new_path = '/work/bb1153/b382267/AQUA/test_zarr/'




def grb2zarr(file = filename, test = None, inline_threshold = 200, save = True, path = new_path):
    """_summary_

    Args:
        file (_type_, optional): _description_. Defaults to filename.
        inline_threshold (int, optional): _description_. Defaults to 200.
        save (bool, optional): _description_. Defaults to True.
        path (_type_, optional): _description_. Defaults to new_path.
    """    
    namewithextension = re.split('/', file)[-1]
    name = re.split(r'\.grb', namewithextension)[0]
    if 'grb' in namewithextension :

        temp = xr.open_dataset(file, engine="cfgrib", chunks='auto', use_cftime= True, decode_cf=False, decode_times=False, decode_timedelta=False)

        temp_cdf = temp.to_netcdf(str(path)+'../NetCDF/'+str(name)+'.nc')

        nc2Zarr(file = str(path)+'../NetCDF/'+str(name)+'.nc', inline_threshold=inline_threshold, save = save, path = path)

    os.system('rm ' +str(path)+'../NetCDF/'+str(name)+'.nc')
    




def nc2Zarr(file = filename, inline_threshold=200, save = True, path = new_path):
    zarray = SingleHdf5ToZarr(h5f=file, inline_threshold=inline_threshold) 
    out = zarray.translate()
    if save:
        namewithextension = re.split('/', file)[-1]
        name = re.split(r'\.nc', namewithextension)[0]
        with open(str(path+str(name))+".json", "w") as outfile:
            json.dump(out, outfile)
        return str(path+str(name))+".json"
    else:
        return  zarray.translate()
    
def multi2Zarr(files, inline_threshold=200, save = True, name = "singleZarr", path = new_path):
    namewithextension = re.split('/', files[0])[-1]
    if 'nc' in namewithextension :
        zarr_files=[]
        for i in range(0, len(files)):
            zarr_file = nc2Zarr(file = files[i], inline_threshold=inline_threshold, save = save, path = path)
            zarr_files.append(zarr_file)
        mzz = MultiZarrToZarr(
            zarr_files,
            concat_dims=["time"]
        )
        out = mzz.translate()
    elif 'json' in namewithextension:
        mzz = MultiZarrToZarr(
            files,
            concat_dims=["time"]
        )
        out = mzz.translate()
    if save:
        filenameSZ = str(path+str(name))+".json"
        with open(filenameSZ, "w") as outfile:
            json.dump(out, outfile)
        return filenameSZ
    else:
        return  out.translate()




def opends(file = filename):
    #if engine=="netcdf4":
    namewithextension = re.split('/', file)[-1]
    if 'nc' in namewithextension :
        ds = xr.open_dataset(
            file, engine="netcdf4"
            )
    #elif engine=="zarr":
    elif 'json' in namewithextension:
        ds = xr.open_zarr(f"reference::{file}" , consolidated=False)
    elif 'grb' in namewithextension:
        ds = xr.open_dataset(
            file, engine="cfgrib"
            )
    return ds 