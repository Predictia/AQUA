#!/usr/bin/env python3
"""Loop on multiple dataset to crete weights using the Reader"""

resos = [True] # ['r025']
measure_time = True

if measure_time:
    import time
    import json

loglevel = 'WARNING'

from aqua import Reader, inspect_catalogue
from aqua.util import ConfigPath
from aqua.logger import log_configure

def append_dict_to_file(file_path, new_dict):
    """
    Appends a dictionary to a JSON file.
    If the file exists, the function loads the existing data from the file,
    appends the new dictionary to the existing list, and writes the updated
    list back to the file. If the file doesn't exist, it creates a new file
    with the provided dictionary.

    Args:
      file_path (str): The path to the JSON file.
      new_dict (dict): The dictionary to append to the file.
    Returns:
      None
    """
    try:
        # Read the existing list from the file
        with open(file_path, 'r') as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or is empty, start with an empty list
        existing_data = []

    # Append the new dictionary to the existing list
    existing_data.append(new_dict)

    # Write the updated list back to the file
    with open(file_path, 'w') as file:
        json.dump(existing_data, file, indent=2)  # indent for pretty formatting
        
def grid_size(data):
    """ Function to get the size of the grid

    Args:
        data (xarray):                  The Dataset

    Returns:
        int:                           The size of the grid
    """
    if 'DataArray' in str(type(data)):
        _size = data.size
    elif 'Dataset' in str(type(data)):
        _names = list(data.dims)
        _names = [name for name in _names if name != 'time']
        _size = 1
        for i in _names:
            _size *= data[i].size
    return _size
     
def generate_catalogue_weights():
    """
    Generates weights for regridding and records the processing time in a catalog.
    This function generates weights for regridding based on the specified parameters.
    If in test mode, it generates weights for a predefined case and records the processing time.
    If not in test mode, it iterates over different model, experiment, source, regridding resolution,
    and zoom level combinations, generates weights, and records the processing time.
    The results are stored in a catalog (data.json) with details such as model, experiment, source,
    regridding resolution, zoom level, and processing time.

    Args:
      loglevel (str): The logging level for the function (default is "INFO").
      measure_time (bool): If True, records the processing time for each operation.
      resos (list): A list of regridding resolutions.

    Returns:
      None
    """
    logger = log_configure(log_level=loglevel, log_name='Weights Generator')
    logger.info('The weight generation is started.')   
    for reso in resos:
        model = inspect_catalogue()
        for m in model:
            exp = inspect_catalogue(model = m)
            for e in exp:
                source = inspect_catalogue(model = m, exp = e)
                for s in source:
                    for zoom in range(0, 9):
                        try:
                            if measure_time:
                                t_1 = time.time()
                                reader = Reader(model=m, exp=e, source=s, regrid=reso, zoom=zoom)
                                t_2 = time.time()
                                data = reader.retrieve()
                                new_dict_to_append = {'model': m, 'exp': e,  'source': s, 'regrid': reso, 'zoom': zoom, 'time': t_2-t_1, 'size': grid_size(data)}
                                append_dict_to_file('weights_calculation_time.json', new_dict_to_append)
                            else:
                                Reader(model=m, exp=e, source=s, regrid=reso, zoom=zoom)
                        except Exception as e:
                            # Handle other exceptions
                            logger.error(f"For the source {m} {e} {s} {reso} {zoom} an unexpected error occurred: {e}")
    
if __name__ == '__main__': 
    generate_catalogue_weights()

