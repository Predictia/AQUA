import os 
import re

from dask_jobqueue import SLURMCluster # pip 
from dask.distributed import Client, progress 

"""Module contain functions to create and control the SLURM job:
     - squeue_user,
     - slurm_interactive_job,
     - pwd,
     - scancel

.. moduleauthor:: AQUA team <natalia.nazarova@polito.it>

"""
def squeue_user(username = "$USER"):
    """Checking the status of a SLURM job

    Args:
        username (str, optional): Name of the user who submitted the job to the queue. Defaults to "$USER".

    Returns:
        str:   The status of all jobs of the user in a SLURM queue
    """
    squeue_user = os.system("squeue --user="+str(username))
    return squeue_user 

def pwd():
    """Printing the full path of current directory

    Returns:
        str:    The full path to your current directory 
    """
    with os.popen("pwd ") as f:
        _pwd = f.readline()
    return re.split(r'[\n]', _pwd)[0]
    

def slurm_interactive_job(cores=1, memory="100 GB", queue = "compute", walltime='04:30:50', jobs=1):
    """Submitting the job to the SLURM queue 

    Args:
        cores (int, optional):      The number of cores per socket. Defaults to 1.
        memory (str, optional):     The real memory required per node. Defaults to "100 GB".
        queue (str, optional):      The name of the queue to which SLURM submits the job. Defaults to "compute".
        walltime (str, optional):   The duration for which the nodes remain allocated to you. Defaults to '04:30:50'.
        jobs (int, optional):       The factor of assignment scaling across multiple nodes. Defaults to 1.
    """
    extra_args=[
        "--error="+str(pwd())+"/slurm/logs/dask-worker-%j.err",
        "--output="+str(pwd())+"/slurm/output/dask-worker-%j.out"
    ]

    cluster = SLURMCluster(
        name='dask-cluster', 
        cores=cores,    
        memory=memory, 
        project="bb1153",
        queue=queue, 
        walltime=walltime,
        job_extra=extra_args,
    )
    client = Client(cluster)
    print(cluster.job_script())
    cluster.scale(jobs=jobs)

def scancel(Job_ID=None):
    """scancel() is used to signal or cancel jobs in the queue

    Args:
        Job_ID (str, optional):     The SLURM_JOB_ID of a job to cancel in the queue. Defaults to None.
    """
    os.system("scancel " +str(Job_ID)) 
