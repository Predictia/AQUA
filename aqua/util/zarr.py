import os
import json
from kerchunk.hdf import SingleHdf5ToZarr
from kerchunk.combine import MultiZarrToZarr

def create_zarr(filelist, outfile):
    """
    Create a Zarr file from a list of HDF5/NetCDF files.

    Args:
        filelist (list): A list of file paths to HDF5 files.
        outfile (str): The path to the output Zarr file.

    Returns:
        None
    """

    singles = [SingleHdf5ToZarr(filepath, inline_threshold=0).translate() for filepath in sorted(filelist)]

    mzz = MultiZarrToZarr(
        singles,
        concat_dims=["time"],
        identical_dims=['lat', 'lon']
    )

    out = mzz.translate()

    # Dump to file
    print('Create json file...')
    if os.path.exists(outfile):
        os.remove(outfile)

    with open(outfile, "w") as outfile:
        json.dump(out, outfile)