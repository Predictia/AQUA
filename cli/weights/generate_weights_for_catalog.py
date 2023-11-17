#!/usr/bin/env python3
"""Loop on multiple dataset to crete weights using the Reader"""

resos = [None] # or specify ['r025', 'r100']

from aqua import Reader
from aqua.slurm import slurm 
from aqua.util import ConfigPath
from aqua.logger import log_configure

if __name__ == '__main__':
    # Initializing the logger
    logger = log_configure(log_level=loglevel, log_name='Weights Submitter')
        
    machine_name = ConfigPath().machine
    # Job initialization 
    if machine_name=='levante':        
        slurm.job(cores=16, memory="200 GB", queue=None, walltime='08:00:00',
            jobs=1, path_to_output='.', loglevel='WARNING')
    elif machine_name=='lumi':
        slurm.job()
    #elif machine_name=='mafalda':
    #    slurm.job()

    waiting_for_slurm_response(10)

    model = inspect_catalogue()

    for i in range(0, 60):
        if get_job_status() == 'R':
            logger.info('The weight weekly submitter is started to run!')
            for reso in resos:
                for m in model:
                    exp = inspect_catalogue(model = m)
                    for e in exp:
                        source = inspect_catalogue(model = m, exp = e)
                        for s in source:
                            for zoom in range(0, 9):
                                reader = Reader(model=m, exp=e, source=s, regrid=reso, zoom=zoom)
            break
        else:
            logger.info('The job is waiting in the queue')
            waiting_for_slurm_response(60)
            

