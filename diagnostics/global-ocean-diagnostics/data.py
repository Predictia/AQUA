# Modules will import some dependencies like Onepass
from modules import *

# AQUA reader. One note: regrider is not working for 3d variables
reader = Reader(model = 'FESOM', exp = 'tco3999-ng5', source="interpolated_global_TS") 
data = reader.retrieve()

# Dropping the variables, which are not required
data=data.drop("latitude")
data=data.drop("longitude")
data=data.drop("ocpt")
data=data.coarsen(lat=30, lon=40).mean()  #Here will not use AQUA regridder, because it's just fake thing

# Renaming the Variables
data=data.rename({"salt":"so"})
data=data.rename({"temp":"thetao"})
data=data.rename({"depth":"lev"})

# Faking some changes in date for our next codes
data = data.resample(time='7.39H').mean() 
time = np.arange('2011-01-01', '2013-01-01', dtype='datetime64[D]')
data["time"]=time
data1=data.resample(time="Y").mean()
data1.to_netcdf("./../../../data.nc")