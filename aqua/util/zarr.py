import os
import json
from kerchunk.hdf import SingleHdf5ToZarr
from kerchunk.combine import MultiZarrToZarr
from aqua import log_configure

def create_zarr(filelist, outfile, loglevel='WARNING'):
    """
    Create a Zarr file from a list of HDF5/NetCDF files.

    Args:
        filelist (list): A list of file paths to HDF5 files.
        outfile (str): The path to the output Zarr file.

    Returns:
        None
    """

    logger = log_configure(log_level=loglevel, log_name='zarr creation')

    logger.info('Creating Zarr file from %s', filelist)
    singles = [SingleHdf5ToZarr(filepath, inline_threshold=0).translate() for filepath in sorted(filelist)]

    logger.info('Combining Zarr files')
    mzz = MultiZarrToZarr(
        singles,
        concat_dims=["time"],
        identical_dims=['lat', 'lon']
    )

    logger.info('Translating Zarr files to json')
    out = mzz.translate()

    # Dump to file
    logger.info('Dumping to file JSON %s', outfile)
    if os.path.exists(outfile):
        os.remove(outfile)
    with open(outfile, "w") as outfile:
        json.dump(out, outfile)