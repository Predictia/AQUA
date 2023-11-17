#!/usr/bin/env python3
"""Loop on multiple dataset to crete weights using the Reader"""

resos = [None] # or specify ['r025', 'r100']

from aqua import Reader
from aqua.slurm import slurm, get_job_status, waiting_for_slurm_response
from aqua.util import ConfigPath
from aqua.logger import log_configure

if __name__ == '__main__':
    
    # Initializing the logger
    loglevel = 'WARNING'
    logger = log_configure(log_level=loglevel, log_name='Weights Submitter')
    
    logger.info('Running weights weekly submitter...')

    # Job initialization 
    if ConfigPath().machine=='levante':        
        slurm.job(cores=16, memory="200 GB", walltime='08:00:00', jobs=1, path_to_output='.', loglevel=loglevel)
    elif ConfigPath().machine=='lumi':
        slurm.job()
    #elif ConfigPath().machine=='mafalda':
    #    slurm.job()

    waiting_for_slurm_response(10)

    model = inspect_catalogue()

    for i in range(0, 120):
        if get_job_status() == 'R':
            logger.info('The weight weekly submitter is started to run!')
            for reso in resos:
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
            break
        else:
            logger.info('The job is waiting in the queue')
            waiting_for_slurm_response(60)

    logger.info('The weights weekly submitter is terminated.')
