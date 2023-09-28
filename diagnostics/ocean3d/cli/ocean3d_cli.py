import sys
import os
import traceback

try:
    sys.path.insert(0, '../../..')
    sys.path.insert(0, '../..')
    from aqua import Reader,catalogue, inspect_catalogue

    from ocean3d import plot_stratification
    from ocean3d import plot_spatial_mld_clim

    from ocean3d import hovmoller_lev_time_plot
    from ocean3d import time_series_multilevs
    from ocean3d import multilevel_t_s_trend_plot
    from ocean3d import zonal_mean_trend_plot

    import xarray as xr
    from aqua.util import load_yaml
    import argparse


    parser = argparse.ArgumentParser(description='Your script description')
    parser.add_argument('--model', type=str, help='Model name')
    parser.add_argument('--exp', type=str, help='Experiment name')
    parser.add_argument('--source', type=str, help='Source name')
    parser.add_argument('--output_dir', type=str, help='Output directory')

    args = parser.parse_args()


    ocean3d_config = load_yaml("../config.yaml")

    output_dir= ocean3d_config["output_dir"]
    model= ocean3d_config["model"]
    exp= ocean3d_config["exp"]
    source= ocean3d_config["source"]

    if args.model:
        model = args.model
    else:
        model = model

    if args.exp:
        exp = args.exp
    else:
        exp = exp

    if args.source:
        source = args.source
    else:
        source = source

    if args.output_dir:
        outputdir = args.outputdir
    else:
        output_dir = output_dir


    if not os.path.exists('output_dir'):
        os.makedirs('output_dir')
    
    print(f"Reader selecting for model= {model},exp= {exp},source= {source}")
    reader = Reader(model, exp, source, fix=True)
    data = reader.retrieve()

    hovmoller_lev_time_plot(data, region= "Global Ocean", anomaly= False,
                            standardise= False, output= True,
                            output_dir= output_dir)

    hovmoller_lev_time_plot(data = data, region= "Global Ocean",
                            anomaly= True, standardise = False,                        
                            anomaly_ref = 'Tmean', output= True,
                            output_dir= output_dir)

    hovmoller_lev_time_plot(data = data, region= "Global Ocean",
                            anomaly= True, standardise = True,                        
                            anomaly_ref = 'Tmean', output= True,
                            output_dir= output_dir)

    time_series_multilevs(data,'Global Ocean', anomaly= False,
                        standardise= False, anomaly_ref="FullValue",
                        customise_level=False, levels=list,output = True,
                        output_dir = output_dir)

    time_series_multilevs(data,'Global Ocean',anomaly= True,
                        standardise= False, anomaly_ref="t0",
                        customise_level=False, levels=list,output = True,
                        output_dir= output_dir)

    multilevel_t_s_trend_plot(data,'Global Ocean', customise_level=False,
                            levels=None,output= True,
                            output_dir =  output_dir)

    plot_stratification(data, region= "Labrador Sea", time = "February",output= True, output_dir= output_dir)
    plot_stratification(data, region= "Labrador Sea", time = "DJF",output= True, output_dir= output_dir)

    plot_spatial_mld_clim(data, region= "labrador_gin_seas", time = "Mar",overlap= True,output= True, output_dir= output_dir)
    plot_spatial_mld_clim(data, region= "labrador_gin_seas", time = "FMA",overlap= True,output= True, output_dir= output_dir)

except KeyError as ke:
    print("there is error")
    print(f"KeyError: {str(ke)}")

except ImportError as ie:
    # Handle ImportError
    print(f"ImportError: {str(ie)}")
    
except Exception as e:
    print("there is error")
    print(f"An error occurred: {str(e)}")
    traceback.print_exc()