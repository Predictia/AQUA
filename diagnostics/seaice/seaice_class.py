import sys
import matplotlib.pyplot as plt
import xarray as xr
from aqua import Reader
from aqua.util import load_yaml
from aqua.logger import log_configure

sys.path.append("../")

"""Sea ice diagnostics"""


class SeaIceExtent:
    """Sea ice extent class"""

    def __init__(self, option=None, configdir=None,
                 loglevel="WARNING"):
        """The SeaIceExtent constructor."""

        # Configure logger
        self.loglevel = loglevel
        self.logger = log_configure(self.loglevel, 'seaice')
        pass

    def run(
        self,
        mySetups=[["IFS", "tco1279-orca025-cycle3", "2D_monthly_native"]],
        myRegions=["Arctic", "Southern Ocean"],
    ):
        """The run diagnostic method. Takes two inputs:
            mySetups    A list of 3-item lists indicating which setups need
            to be plotted. A setup = model, experiment, source

            myRegions   A list of regions available in the regions.yml file

            The method produces as output a figure with the seasonal cycles
            of sea ice extent in the regions for the setups"""
        # define the internal logger
        self.logger = log_configure(log_level="info", log_name='Reader')

        # Load regions information
        # with open("../regions.yml") as f:
        #     regionDict = yaml.safe_load(f)
        regionDict = load_yaml("../regions.yml")

        nRegions = len(myRegions)
        thresholdSeaIceExtent = 0.15

        # Instantiate the various readers (one per setup) and retrieve the
        # corresponding data
        myExtents = list()
        for js, setup in enumerate(mySetups):
            model, exp, source = setup[0], setup[1], setup[2]

            label = model + " " + exp + " " + source

            # Instantiate reader
            reader = Reader(model=model, exp=exp, source=source)

            self.logger.info("\t".join([s.ljust(20) for s in setup]))
            data = reader.retrieve()

            if model == "OSI-SAF":
                data = data.rename({"siconc": "ci"})

            areacello = reader.grid_area
            lat = data.coords["lat"]
            lon = data.coords["lon"]

            # Important: recenter the lon in the conventional 0-360 range
            lon = (lon + 360) % 360
            lon.attrs["units"] = "degrees"

            # Create mask based on threshold
            ci_mask = data.ci.where((data.ci > thresholdSeaIceExtent) &
                                    (data.ci < 1.0))

            regionExtents = list()  # Will contain the time series for each
            # region and for that setup
            # Iterate over regions
            for jr, region in enumerate(myRegions):

                self.logger.info("\tProducing diagnostic for region " + region)
                # Create regional mask
                latS, latN, lonW, lonE = (
                    regionDict[region]["latS"],
                    regionDict[region]["latN"],
                    regionDict[region]["lonW"],
                    regionDict[region]["lonE"],
                )

                # Dealing with regions straddling the 180° meridian
                if lonW > lonE:
                    regionMask = (
                        (lat >= latS)
                        & (lat <= latN)
                        & ((lon >= lonW) | (lon <= lonE))
                    )
                else:
                    regionMask = (
                        (lat >= latS)
                        & (lat <= latN)
                        & (lon >= lonW)
                        & (lon <= lonE)
                    )

                # Print area of region

                if source == "lra-r100-monthly" or model == "OSI-SAF":
                    if source == "lra-r100-monthly":
                        dim1Name, dim2Name = "lon", "lat"
                    elif model == "OSI-SAF":
                        dim1Name, dim2Name = "xc", "yc"
                    myExtent = areacello.where(regionMask).where(
                        ci_mask.notnull()).sum(dim=[dim1Name, dim2Name]) / 1e12
                else:
                    myExtent = areacello.where(regionMask).where(
                        ci_mask.notnull()).sum(dim="value") / 1e12

                myExtent.attrs["units"] = "million km^2"
                myExtent.attrs["long_name"] = "Sea ice extent"
                regionExtents.append(myExtent)

            # Save set of diagnostics for that setup
            myExtents.append(regionExtents)

        # Produce figure and create NetCDF
        fig, ax = plt.subplots(nRegions, figsize=(13, 3 * nRegions))

        for jr, region in enumerate(myRegions):
            for js, setup in enumerate(mySetups):
                label = " ".join([s for s in setup])
                extent = myExtents[js][jr]

                # Don't plot the obs nh if the region is in sh and conversely

                # Don't plot osisaf nh in the south and conversely
                if (setup[0] == "OSI-SAF" and setup[2][:2] == "nh" and
                    regionDict[region]["latN"] < 20.0) or (
                        setup[0] == "OSI-SAF" and setup[2][:2] == "sh"
                        and regionDict[region]["latS"] > -20.0):
                    pass
                else:
                    ax[jr].plot(extent.time, extent, label=label)

                    
            ax[jr].set_title("Sea ice extent: region " + region)

            ax[jr].legend()
            ax[jr].set_ylabel(extent.units)
            ax[jr].grid()


        fig.tight_layout()
        for fmt in ["png", "pdf"]:
            fig.savefig("./figSIE." + fmt, dpi=300)

        # NetCDF creation (one per setup)
        for js, setup in enumerate(mySetups):
            dataset = xr.Dataset()
            label = " ".join([s for s in setup])
            for jr, region in enumerate(myRegions):

                if (setup[0] == "OSI-SAF" and setup[2][:2] == "nh" and
                    regionDict[region]["latN"] < 20.0) or (
                        setup[0] == "OSI-SAF" and setup[2][:2] == "sh"
                        and regionDict[region]["latS"] > -20.0):
                    pass
                else:
                    # NetCDF variable
                    varName = f"{setup[0]}_{setup[1]}_{setup[2]}_{region}"
                    dataset[varName] = myExtents[js][jr]
                    dataset.to_netcdf("__".join([s for s in setup]) + ".nc")