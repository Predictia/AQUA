import os
import xarray as xr

def clean_files(filelist):
    """
    Removes the specified files from the filesystem.

    Args:
    - filelist (str or list): A single filename or a list of filenames to be removed.

    Returns:
        None

    """
    if isinstance(filelist, str):
        filelist = [filelist]

    for fileout in filelist :
        if os.path.exists(fileout):
            os.remove(fileout)

def lonlatbox(lon, lat, delta) : 
    """
    Define the list for the box to retain high res data in the vicinity of the TC centres

    Args:
        lon: longitude of the TC centre
        lat: latitude of the TC centre
        delta: length in degrees of the lat lon box

    Returns: 
       box: list with the box coordinates
    """
    return [float(lon) - delta, float(lon) +delta, float(lat) -delta, float(lat) + delta]

def write_fullres_field(gfield, filestore): 

    """
    Writes the high resolution file (netcdf) format with values only within the box
    Args:
        gfield: field to write
        filestore: file to save
    """

    time_encoding = {'units': 'days since 1970-01-01',
                 'calendar': 'standard',
                 'dtype': 'float64'}
    var_encoding = {"zlib": True, "complevel": 1}
    if isinstance(gfield, int):
        print(f"No tracks to write")
    else:
        gfield.where(gfield!=0).to_netcdf(filestore,  encoding={'time': time_encoding, gfield.name: var_encoding})
        gfield.close()
