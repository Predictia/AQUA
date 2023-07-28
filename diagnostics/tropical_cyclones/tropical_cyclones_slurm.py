#!/usr/bin/env python3

"""CLI interface to run the TempestExtemes TCs tracking"""

import pandas as pd
import numpy as np
import xarray as xr
import sys

sys.path.insert(0, '../')

from tropical_cyclones import TCs
from aqua.util import load_yaml
from aqua.logger import log_configure

mainlogger = log_configure('INFO', log_name='MAIN')

if __name__ == '__main__':

    # load the config file
    tdict = load_yaml('config/config_tcs.yaml')

    # initialise tropical class with streaming options
    tropical = TCs(tdict=tdict, streaming=True, 
                    stream_step=tdict['stream']['streamstep'], 
                    stream_unit="days", 
                    stream_startdate=tdict['time']['startdate'], 
                    loglevel = "INFO",
                    nproc=1)
    
    tropical.loop_streaming(tdict)