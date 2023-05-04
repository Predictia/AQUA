# Loading the necessary modules 

import xarray as xr # To create a Dataset
import pickle  # To save the Dataset to memory
from aqua import Reader, catalogue

reader = Reader(model="IFS", exp="tco2559-ng5", source="ICMGG_atm2d")

import sys
sys.path.insert(0, '../')
from src.trop_prec_diagnostic import TR_PR_Diagnostic as TR_PR_Diag
diag = TR_PR_Diag(trop_lat = 10,  num_of_bins = 15, first_edge = 0, width_of_bin = 1*10**(-6)/15)

# Path to folder, where we want to store the results 
path = '.'

# The number of weeks 
num=3

for i in range(0, num):
    # Reading one week of data
    week  = reader.retrieve(streaming=True,  stream_unit = 'weeks',  regrid=True ) 
    # Counts-histogram of tropical precipitaion
    hist_ifs_week = diag.hist1d_fast(week)

    tprate_dataset = hist_ifs_week.to_dataset(name="trop_counts")
    tprate_dataset.attrs = week.attrs
    with open(str(path)+'ifs_'+str(i)+'_week_tprate.pickle', 'wb') as output:
        pickle.dump(tprate_dataset, output)


# Reading and Summing
with open(str(path)+'ifs_1week_tprate.pickle', 'rb') as data:
    dataset_total = pickle.load(data)
with open(str(path)+'ifs_2week_tprate.pickle', 'rb') as data:
    dataset_2 = pickle.load(data)
with open(str(path)+'ifs_3week_tprate.pickle', 'rb') as data:
    dataset_3 = pickle.load(data)

dataset_total =+ dataset_2 
dataset_total =+ dataset_3

dataset_total



