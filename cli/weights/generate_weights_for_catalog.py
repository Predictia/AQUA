#!/usr/bin/env python3
"""Loop on multiple dataset to crete weights using the Reader"""

resos = [None] # or specify ['r025', 'r100']
test_mode = True

import sys
from aqua import Reader, inspect_catalogue
from aqua.slurm import slurm, get_job_status, waiting_for_slurm_response
from aqua.util import ConfigPath
from aqua.logger import log_configure

def generate_catalogue_weights(loglevel='WARNING'):
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
                            reader = Reader(model=m, exp=e, source=s, regrid=reso, zoom=zoom)
                        except Exception as e:
                            # Handle other exceptions
                            logger.error(f"For the source {m} {e} {s} {reso} {zoom} an unexpected error occurred: {e}")
                            
def job_initialization(loglevel='WARNING'):
    logger = log_configure(log_level=loglevel, log_name='Weights Submitter')
    # Job initialization 
    if ConfigPath().machine=='levante':        
        slurm.job() #cores=16, memory="200 GB", walltime='08:00:00', jobs=1, path_to_output='.', loglevel=loglevel)
    elif ConfigPath().machine=='lumi':
        slurm.job()
    waiting_for_slurm_response(10)
    logger.info('The weights submitter is submitted to the queue.')
    
def generate_catalogue_weights_on_slurm(loglevel='WARNING'):
    logger = log_configure(log_level=loglevel, log_name='Weights Submitter')
    for i in range(0, 120):
        if get_job_status() == 'R':
            if test_mode:
                logger.info('TEST.')
                waiting_for_slurm_response(10)
            else:
                generate_catalogue_weights(loglevel=loglevel)
            break
        else:
            logger.info('The job is waiting in the queue.')
            waiting_for_slurm_response(60)
    logger.info('The weights submitter is terminated.')
    

if __name__ == '__main__':
    # Initializing the logger
    if test_mode:
        loglevel = 'info'
        logger = log_configure(log_level=loglevel, log_name='Weights Submitter')
    else:
        loglevel = 'WARNING'
    
    if ConfigPath().machine=='levante' or ConfigPath().machine=='lumi':
        job_initialization(loglevel=loglevel)
        generate_catalogue_weights_on_slurm(loglevel=loglevel)
        sys.exit("Exiting the script")
    else:
        if test_mode:
            logger.info('TEST.')
            waiting_for_slurm_response(10)
        else:
            generate_catalogue_weights(loglevel=loglevel)
            sys.exit("Exiting the script")

