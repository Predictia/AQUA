#!/usr/bin/env python3
"""Loop on multiple dataset to crete weights using the Reader"""

import sys
from aqua import Reader, inspect_catalogue
from aqua.logger import log_configure

loglevel = 'WARNING'
logger = log_configure(log_level=loglevel, log_name='Weights Generator')

resos = ['r025', 'r100']

full_catalogue=False
# example 
model = []  # ['FESOM']
exp = []    # ['tco2559-ng5-cycle3']
source = [] # ['3D_daily_native', '2D_daily_native', '2D_monthly_native_elem']

if not full_catalogue and len(model) == 0 or len(exp)==0 or len(source)==0:
    logger.error(f"If you do not want to generate the weights for the entire catalog, "
      f"you must provide the models, experiments, and sources list.")
    sys.exit(1)
    
logger.info('The weight generation is started.')   

for reso in resos:
        model = inspect_catalogue() if full_catalogue else model
        for m in model:      
            exp = inspect_catalogue(model = m) if full_catalogue else exp
            for e in exp:
                source = inspect_catalogue(model = m, exp = e) if full_catalogue else source
                for s in source:
                    for zoom in range(0, 9):
                        try:
                            Reader(model=m, exp=e, source=s, regrid=reso, zoom=zoom)
                        except Exception as e:
                            # Handle other exceptions
                            logger.error(f"For the source {m} {e} {s} {reso} {zoom} an unexpected error occurred: {e}")
