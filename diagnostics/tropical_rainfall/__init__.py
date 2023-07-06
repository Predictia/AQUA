""" The tropical rainfall module"""

from .tropical_rainfall_class import Tropical_Rainfall
from .tropical_rainfall_func import time_interpreter
from .tropical_rainfall_func import convert_length, convert_time, unit_splitter, extract_directory_path

__version__ = '0.0.1'

__all__ = ['Tropical_Rainfall', 'time_interpreter', 
           'convert_length',    'convert_time', 'unit_splitter', 'extract_directory_path']

# Change log
# 0.0.1: Initial version