# Importing the aqua.slurm module and slurm supporting functions nedeed for your script
from aqua.slurm import slurm 
from slurm_supporting_func import get_job_status, waiting_for_slurm_response

####################################################################
import sys
from aqua import Reader
sys.path.insert(0, '../../')
from tropical_rainfall import Tropical_Rainfall
####################################################################

# Specify the amount of memory, cores which you would like to use during the run!
# By default, slurm.job(cores=1, memory="10 GB", queue = "compute", walltime='02:30:00', jobs=1)
# The default setup can be not enough for your calculations

slurm.job()

# The meaning of the loop is the following: 
# The aqua.slurm module submitted your job to the queue. But you do not want to start your calculations 
# since your job is waiting in the queue and not running yet. Each iteration in the loop checks the status 
# of your job once per minute. If your job was successfully launched to the node and got the running status, 
# your calculations will also start to run. 
 
for i in range(0, 60):
    if get_job_status() == 'R':
        print('The job is started to run!')
        ##############################################################
        reader          = Reader(model="ICON", exp="ngc3028", source="lra-r100-monthly", regrid = "r100")
        icon_ngc3028    = reader.retrieve()

        diag = Tropical_Rainfall(trop_lat=15,  num_of_bins = 20, first_edge = 0, width_of_bin = 1*10**(-3)/40)

        path_to_netcdf = "/work/bb1153/b382267/tropical_rainfall_cicle3/NetCDF/histograms/"

        hist_icon_ngc3028 = diag.histogram(icon_ngc3028, path_to_histogram=path_to_netcdf, name_of_file="TEST_CLI")
        ##############################################################
        break
    else:
        print('The job is waiting in the queue')
        waiting_for_slurm_response(60)

# Note: The loop will stop to check your job status only for one hour. If the queue is busy, 
# consider increasing the range of your loop.