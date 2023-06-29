

"""Sea ice diagnostics """

class SeaIceExtent():


    """Sea ice extent class"""
    def __init__(self, option=None, configdir=None):
        """The SeaIceExtent constructor."""

    def run(self, mySetups = [["IFS",     "tco1279-orca025-cycle3",   "2D_monthly_native"     ]]):
        """The run diag method."""
        

        from    aqua import Reader,catalogue, inspect_catalogue
        import  datetime
        import  xarray as xr
        import  numpy as np
        import  matplotlib.pyplot as plt

        # Parameters,  to be moved in a YAML file eventually
                       # Region name          # southernmost latitude    # northernmost latitude   # westernmost longitude # easternmost longitude
        regions = [ \
                       [ "Arctic",            [0.0,                      90.0,                     0.0,                    360.0                 ]], \
                       [ "Hudson Bay",        [50.0,                     63.0,                     265.0,                  285.0                 ]], \
                       [ "Southern Ocean",    [-90.0,                    0.0,                      0.0,                    360.0                 ]], \
                       [ "Ross Sea",          [-90.0,                    0.0,                      160.0,                  230.0                 ]], \
                       [ "Amundsen-Bellingshausen Seas", [-90.0,         0.0,                      230.0,                  300.0                 ]], \
                       [ "Weddell Sea",       [-90.0,                    0.0,                      300.0,                  20.0                  ]], \
                       [ "Indian Ocean",      [-90.0,                    0.0,                      20.0,                   90.0                  ]], \
                       [ "Pacific Ocean",     [-90.0,                    0.0,                      90.0,                   160.0                 ]], \
                    ]
        nRegions = len(regions)
        thresholdSeaIceExtent = 0.15


        # Instantiate the various readers (one per setup) and retrieve the corresponding data
        myReaders = list()
        myData    = list()
        myExtents = list()
        for js, setup in enumerate(mySetups):
            model, exp, source = setup[0], setup[1], setup[2]
            
            label = model + " " + exp + " " + source

            # Instantiate reader
            reader = Reader(model  = model, \
                        exp    = exp,   \
                        source = source,\
                    )
            
            myReaders.append(reader)

            print("Retrieving " + "\t".join([s.ljust(20) for s in setup]))
            data = reader.retrieve()
            myData.append(data)
            
            # Renames
            data=data.rename({"ci":"siconc"})


            areacello = reader.grid_area
            lat = data.coords["lat"]
            lon = data.coords["lon"]

            # Create mask based on threshold
            siconc_mask = data.siconc.where(data.siconc > thresholdSeaIceExtent).where(data.siconc < 1.0)

            regionExtents = list() # Will contain the time series for each region and for that setup
            # Iterate over regions
            for jr, region in enumerate(regions):

                print("\tProducing diagnostic for region " + region[0])
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
                
                if source == "lra-r100-monthly" or model == "OSI-SAF":
                    if source == "lra-r100-monthly":
                        dim1Name, dim2Name = "lon", "lat"
                    elif model == "OSI-SAF":
                        dim1Name, dim2Name = "xc", "yc"
                    myExtent = areacello.where(regionMask).where(siconc_mask.notnull()).sum(dim = [dim1Name, dim2Name]) / 1e12
                else:
                    myExtent = areacello.where(regionMask).where(siconc_mask.notnull()).sum(dim = "value") / 1e12

                myExtent.attrs["units"] = "million km^2"
                myExtent.attrs["long_name"] = "Sea ice extent"
                regionExtents.append(myExtent)

            # Save set of diagnostics for that setup
            myExtents.append(regionExtents)


        # Produce figure
        # Print region area for information
        #areaRegion = areacello.where(regionMask).sum()
        #print(region[0] + " region area: " + str(areaRegion.data) + areaRegion.units)
        sideSubPlot = int(np.ceil(np.sqrt(nRegions)))
        print(sideSubPlot)
        fig, ax = plt.subplots(sideSubPlot, sideSubPlot, figsize = (16, 12))
        for js, setup in enumerate(mySetups):
            label = " ".join([s for s in setup])
            for jr, region in enumerate(regions):

                extent = myExtents[js][jr]

                jx = jr // sideSubPlot
                jy = jr %  sideSubPlot

            
                ax[jx, jy].plot(extent.time, extent, label = label)
            
                ax[jx,jy].set_title("Sea ice extent: region " + region[0])
        
                ax[jx,jy].legend()
                ax[jx,jy].set_ylabel(extent.units)
                ax[jx,jy].grid()
        fig.tight_layout()
        fig.savefig("./figExtent.png")
        

        # A few maps
        #import cartopy.crs as ccrs
        #import matplotlib.pyplot as plt


        #subplot_kws=dict(projection=ccrs.NorthPolarStereo(central_longitude=-30.0),
        #                facecolor='grey')

        #fig, ax = plt.subplots(1, 1, figsize = (8, 8))
        #p = ax.plot(lon,lat, data.siconc.mean(),
        #                vmin=0, vmax=1,
        #                cmap=plt.cm.Blues,
        #                subplot_kws=subplot_kws,
        #                transform=ccrs.PlateCarree(),
        #                add_labels=False,
        #                add_colorbar=False)

        # add separate colorbar
        #cb = plt.colorbar(p, ticks=[-2,0,2,4,6,8,10,12], shrink=0.99)
        #cb.ax.tick_params(labelsize=18)

        #p.axes.gridlines(color='black', alpha=0.5, linestyle='--')
        #p.axes.set_extent([-300, 60, 50, 90], ccrs.PlateCarree())