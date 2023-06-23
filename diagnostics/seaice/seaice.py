from aqua import Reader,catalogue, inspect_catalogue
import datetime
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

#cat = catalogue()

# Parameters to be moved to a YAML file eventually
                       # Region name          # southernmost latitude    # northernmost latitude   # westernmost longitude # easternmost longitude
regions = [ \
                       [ "Arctic",            [0.0,                      90.0,                     0.0,                    360.0                 ]], \
                       [ "Southern Ocean",    [-90.0,                    0.0,                      0.0,                    360.0                 ]], \
                       [ "Hudson Bay",        [50.0,                     63.0,                     265.0,                  285.0                 ]], \
                       [ "Ross Sea",          [-90.0,                    0.0,                      160.0,                   230.0                ]], \
                       [ "Amundsen-Bellingshausen Seas", [-90.0,         0.0,                      230.0,                  300.0                 ]], \
                       [ "Weddell Sea",       [-90.0,                    0.0,                      300.0,                  20.0                  ]], \
                       [ "Indian Ocean",      [-90.0,                    0.0,                      20.0,                   90.0                  ]], \
                       [ "Pacific Ocean",     [-90.0,                    0.0,                      90.0,                   160.0                 ]], \
                    ]

thresholdSeaIceExtent = 0.15
computeGridCellAreas  = True # Whether or not to compute grid cell areas from the lat-lon information

# Works
model = "IFS"
exp   = "tco1279-orca025-cycle3"
source= "lra-r100-monthly"
computeGridCellAreas  = True

# in test
model = "FESOM"
exp   = "tco2559-ng5-cycle3"
source= "lra-r100-monthly"

model = "OSI-SAF"
exp   = "osi-450"
source = "nh"
fix   = True

computeGridCellAreas  = False

reader = Reader(model  = model, \
                exp    = exp,   \
                source = source,\
               )

data = reader.retrieve(fix = fix)

if computeGridCellAreas:
    # Create grid cell areas
    # Ensure that the grid is really regular
    if len(data.lon.shape) != 1 or len(data.lat.shape) != 1 \
      or len(set(np.diff(data.lon))) != 1 or len(set(np.diff(data.lat))) != 1:
        print("Lat and lon are not regular")
        stop
    else:

        # Broadcast lat and lon to 2-D arrays
        lon, lat = xr.broadcast(data.lon, data.lat)

        dlam = np.diff(data.lon)[0] * 2 * np.pi / 360.0 # Degrees to radians
        dphi = np.diff(data.lat)[0] * 2 * np.pi / 360.0 # Degrees to radians

        phi = 2 * np.pi / 360.0 * data.lat
        lam = 2 * np.pi / 360.0 * data.lon

        # Expand grid
        lam, phi = xr.broadcast(data.lon / 360.0 * 2 * np.pi, data.lat / 360.0 * 2 * np.pi)
 

        Rearth = 6356e3 # meters

        areacello = np.cos(phi) * Rearth * dlam * Rearth * dphi / 1e12
        areacello = areacello.rename("areacello")
        areacello.attrs["units"] = "million km^2"
        areacello.attrs["standard_name"] = "Grid cell area"

        # Check that sum is within the true Earth surface
        trueEarthSurface = 510072000e6 # Wikipedia
        if np.abs((areacello.sum() - trueEarthSurface) / trueEarthSurface) > 0.01:
            print("Earth's surface wrongly calculated")

# Mask based on threshold
ci_mask = data.ci.where(data.ci > thresholdSeaIceExtent).where(data.ci < 1.0)


# Iterate over regions 
for jr, region in enumerate(regions):

    # Create regional mask
    latS, latN, lonW, lonE = regions[jr][1][0], regions[jr][1][1], regions[jr][1][2], regions[jr][1][3]

    # Dealing with regions straddling the 180° meridian
    if lonW > lonE:
        regionMask = (lat >= latS) & (lat <= latN) & ((lon >= lonW) | (lon <= lonE))
    else:
        regionMask = (lat >= latS) & (lat <= latN) & (lon >= lonW) & (lon <= lonE)



    areacello_mask = areacello.where(regionMask)

    
    # Create masks for summing later on
    areacello_mask = areacello.where(regionMask)

    extent = areacello.where(regionMask).where(ci_mask.notnull()).sum(dim = ["lon", "lat"])

    # Print region area for information
    areaRegion = areacello.where(regionMask).sum()
    print(region[0] + " region area: " + str(areaRegion.data) + areaRegion.units)
    fig, ax = plt.subplots(1, 1)
    extent.plot()
    ax.set_title("Sea ice extent: region " + region[0])
    regionNameNoSpace = "".join(region[0].split())
    fig.savefig("./fig_" + regionNameNoSpace + ".png")
