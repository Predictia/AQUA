
import numpy as np
import matplotlib.pyplot as plt
import netCDF4 as nc
from datetime import datetime
import matplotlib.dates as mdates


from seaice_commondiags import *

from netCDF4 import Dataset

rootDir = "/work/bm1235/a270046/cycle2-sync/monthly_means/2.8km/"
fileIn  = "ci_2.8km.nc"

f = Dataset(rootDir + fileIn, mode = "r")


# Read time information
timeVar = f.variables["time"]

units    = timeVar.units
calendar = timeVar.calendar

dates = [datetime.strptime(str(d),'%Y-%m-%d %H:%M:%S') for d in nc.num2date(timeVar, units)]

# Read grid information
lon = f.variables["lon"][:]
lat = f.variables["lat"][:]

dLon = np.mean(np.diff(lon))
if np.any(np.diff(lon) != dLon):
    print("STOP: Lon array not regular")

dLat = np.mean(np.diff(lat))
if np.any(np.diff(lat) != dLat):
    print("STOP: Lat array not regular")

# Make grid cell area 
LON, LAT = np.meshgrid(lon, lat)

R = 6356e3 # Earth radius
cellarea = R * np.cos(LAT / 360.0 * 2 * np.pi) * (dLon / 360.0 * 2 * np.pi)  * R * (dLat / 360.0 * 2 * np.pi)

# Read sea ice information
ci = f.variables["ci"][:]

# Convert in %
ci *= 100

# Call function in seaice_commondiags
extent = compute_extent(ci, cellarea, threshold = 15.0, mask = (LAT > 0))

f.close()


# Plots
fig , ax = plt.subplots(1, 1)
ax.plot(dates, extent)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_title("Arctic sea ice extent\n file " + rootDir + fileIn)
ax.set_ylabel("Million km$^2$")
fig.tight_layout()
fig.savefig("./fig.png")


