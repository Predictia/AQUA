import datetime
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import diag_functions as fn

def wgt_area_mean(data, latN: float, latS: float,
                  lonW: float, lonE: float):

    data=data.sel(lat=slice(latN,latS), lon=slice(lonW,lonE))
    t3gw=data.weighted(np.cos(np.deg2rad(data.lat)))
    wgted_mean=t3gw.mean(("lat","lon"))
    return wgted_mean

def std_anom_from_initial(data, latN: float, latS: float,
                  lonW: float, lonE: float,):
    std_anomaly = xr.Dataset()
    wgted_mean=wgt_area_mean(data, latN, latS, lonW, lonE)
    for var in list(data.data_vars.keys()):
        anomaly_from_initial=wgted_mean[var]-wgted_mean[var][0,]
        std_anomaly[var]= anomaly_from_initial/anomaly_from_initial.std("time")

    return std_anomaly


def thetao_so_anom_plot(data, title):
    # And we perform the corresponding hovmoller plot
    fig, (ax1, ax2) = plt.subplots(nrows=1,ncols=2,
                            figsize=(14,5))
    fig.suptitle(title, fontsize=16)

    tgt=data.thetao.transpose()

    tgt.plot.contourf(levels=12,ax=ax1)
    tgt.plot.contour(colors="black",levels=12,linewidths=0.5,ax=ax1)
    ax1.set_title("Temperature", fontsize=14)
    ax1.set_ylim((5500,0))
    ax1.set_ylabel("Depth (in m)",fontsize=12)
    ax1.set_xlabel("Time (in years)",fontsize=12)

    sgt=data.so.transpose()
    sgt.plot.contourf(levels=12, ax=ax2)
    sgt.plot.contour(colors="black",levels=12,linewidths=0.5, ax=ax2)
    ax2.set_title("Salinity", fontsize=14)
    ax2.set_ylim((5500,0))
    ax2.set_ylabel("Depth (in m)",fontsize=12)
    ax2.set_xlabel("Time (in years)",fontsize=12)

    # plt.savefig('Hovmoller-Global-standardized-anomalies.png',transparent=True)
    return

def time_series(data, title):
    # We now produce timeseries for GLOBAL temperature and salinity standardised anomalies at selected levels
    fig, (ax1, ax2) = plt.subplots(nrows=1,ncols=2,
                            figsize=(14,5))

    fig.suptitle(title, fontsize=16)
    
    levels=[0,100,500,1000,2000,3000,4000,5000]
    for level in levels:
        if level!=0:        
            data_level=data.sel(lev=slice(None, level)).isel(lev=-1) 
        else:
            data_level=data.isel(lev=0)
        data_level.thetao.plot.line(ax=ax1)
        data_level.so.plot.line(ax=ax2)
        
    ax1.set_title("Temperature", fontsize=14)
    ax1.set_ylabel("Standardised Units (at the respective level)",fontsize=12)
    ax1.set_xlabel("Time (in years)",fontsize=12)
    ax1.legend(["0","100","500","1000","2000","3000","4000","5000"], loc='best')

    ax2.set_title("Salinity", fontsize=14)
    ax2.set_ylabel("Standardised Units (at the respective level)",fontsize=12)
    ax2.set_xlabel("Time (in years)",fontsize=12)
    # ax1.set_legend(["0","100","500","1000","2000","3000","4000","5000"], loc='best')
    plt.legend(["0","100","500","1000","2000","3000","4000","5000"], loc='best')
    # plt.savefig('Timeseries-Global-standardized-anomalies.png',transparent=True)
    return

