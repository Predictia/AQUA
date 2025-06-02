import os
import gc

import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from aqua.logger import log_configure
from aqua.util import create_folder
#from dask import compute
from aqua.graphics import plot_single_map

xr.set_options(keep_attrs=True)

class EnsembleTimeseries():
    """
    This class computes mean and standard deviation of the ensemble.mulit-model ensemble. 
    This also plots ensemble mean and standard deviation.  
    """
    def __init__(self,var=None,
                 mon_model_dataset=None,
                 ann_model_dataset=None,
                 mon_ref_data=None,
                 ann_ref_data=None,
                 ensemble_dimension_name="Ensembles",outputdir='./',
                 loglevel='WARNING', **kwargs):
        """
        Args:
            var (str): Variable name.
            mon_model_dataset: xarray Dataset of ensemble members of monthly timeseries.
                     The ensemble memebers are concatenated along a new dimension "Ensmebles".
                     This can be editted with the function edit_attributes.
            ann_model_dataset: xarray Dataset of ensemble members of annual timeseries.
                     Similarly, the members are concatenated along the dimension "Ensembles" 
            ensemble_dimension_name="Ensembles" (str): a default name given to the
                     dimensions along with the individual Datasets were concatenated.
            mon_ref_data: xarray Dataset of monthly reference data.
            ann_ref_data: xarray Dataset of annual reference data.
            outputdir (str): String input for output path.
            loglevel (str): Log level. Default is "WARNING".
            **kwargs (dict): dictonary contains options for plots. Defaults values have been set already.
        """
        self.loglevel = loglevel
        self.logger = log_configure(log_level=self.loglevel, log_name='Ensemble Timeseries')
        self.var = var
        self.dim = ensemble_dimension_name
        self.mon_model_dataset = mon_model_dataset
        self.ann_model_dataset = ann_model_dataset
        self.mon_ref_data = mon_ref_data
        self.ann_ref_data = ann_ref_data
        self.mon_dataset_mean = None
        self.mon_dataset_std = None
        self.ann_dataset_mean = None
        self.ann_dataset_std = None
        self.outputdir = outputdir + 'Ensemble_Timeseries'
        self.outfile = f'ensemble_time_series_timeseries_{self.var}'
        
        self.figure = None
        plot_options = kwargs.get('plot_options',{})
        self.plot_label = plot_options.get('plot_label',True)
        self.plot_std =  plot_options.get('plot_std',True)
        self.plot_ensemble_members = plot_options.get('plot_ensemble_members',True)
        self.plot_ref = plot_options.get('plot_ref',True)
        self.figure_size = plot_options.get('figure_size',[10, 5])
        self.label_size = plot_options.get('label_size',7.5)
        self.ensemble_label = plot_options.get('ensemble_label','Ensemble')
        self.ref_label = plot_options.get('ref_label','ERA5')
        self.plot_title = plot_options.get('plot_title','Ensemble statistics for '+self.var)
        self.label_ncol = plot_options.get('label_ncol',3)
        self.units = plot_options.get('units',None) # TODO
    
    def compute_statistics(self):
        """
        A function to compute the mean and standard devivation of the input dataset
        It is import to make sure that the dim along which the mean is compute is correct.
        The default dim="Ensembles". The DASK's .compute() function is also used here.
        """
        if self.mon_model_dataset != None:
            self.mon_dataset_mean = self.mon_model_dataset[self.var].mean(dim=self.dim)
        if self.ann_model_dataset != None:
            self.ann_dataset_mean = self.ann_model_dataset[self.var].mean(dim=self.dim)

        if self.mon_model_dataset != None:
            self.mon_dataset_std = self.mon_model_dataset[self.var].std(dim=self.dim)
        if self.ann_model_dataset != None:
            self.ann_dataset_std = self.ann_model_dataset[self.var].std(dim=self.dim)

        # TODO: Does it make sence to apply DASK's .compute() here?
        #if self.mon_model_dataset != None:
        #    self.mon_dataset_mean = self.mon_model_dataset[self.var].mean(dim=self.dim).compute()
        #if self.ann_model_dataset != None:
        #    self.ann_dataset_mean = self.ann_model_dataset[self.var].mean(dim=self.dim).compute()

        #if self.mon_model_dataset != None:
        #    self.mon_dataset_std = self.mon_model_dataset[self.var].std(dim=self.dim).compute()
        #if self.ann_model_dataset != None:
        #    self.ann_dataset_std = self.ann_model_dataset[self.var].std(dim=self.dim).compute()

    def plot(self):
        """
        This plots the ensemble mean and standard deviation of the ensemble statistics.
        In this method, it is also possible to plot the individual ensemble members.
        The difference between the timesereis diagnostics plotting methods and this plot() method is that, 
        this method plots annual, monthly ref and model data along with modelled data's +/- 2 x STD around the mean.
        It does not plots +/- 2 x STD for the referene. And, the reason is to show the spread between multi-model/ensembles of the same model.
        """
        self.logger.info('Plotting the ensemble timeseries')
        plt.rcParams["figure.figsize"] = (self.figure_size[0], self.figure_size[1])
        fig, ax = plt.subplots(1, 1)
        color_list = ["#1898e0", "#8bcd45", "#f89e13", "#d24493", "#00b2ed", "#dbe622",
                      "#fb4c27", "#8f57bf", "#00bb62", "#f9c410", "#fb4865", "#645ccc"]
        
        # Plotting monthly ensemble data
        if self.mon_dataset_mean is not None:
            if isinstance(self.mon_dataset_mean,xr.Dataset):
                self.mon_dataset_mean = self.mon_dataset_mean[self.var]
            else:
                self.mon_dataset_mean = self.mon_dataset_mean
            if isinstance(self.mon_dataset_std,xr.Dataset):
                self.mon_dataset_std = self.mon_dataset_std[self.var]
            else:
                self.mon_dataset_std = self.mon_dataset_std
            self.mon_dataset_mean.plot(ax=ax, label=self.ensemble_label+'-mon-mean', color=color_list[0], zorder=2)
            if self.plot_std:
                ax.fill_between(self.mon_dataset_mean.time, self.mon_dataset_mean - 2.*self.mon_dataset_std, self.mon_dataset_mean +
                                2.*self.mon_dataset_std, facecolor=color_list[0], alpha=0.25, label=self.ensemble_label+'-mon-mean'+r'$\pm2$std', zorder=0)
            if self.plot_ensemble_members:
                for i in range(0,len(self.mon_model_dataset[self.var][:,0])):
                    self.mon_model_dataset[self.var][i, :].plot(ax=ax, color='grey', lw=0.7, zorder=1)
        
        # Plotting monthy reference
        if self.mon_ref_data is not None:
            if isinstance(self.mon_ref_data,xr.Dataset):
                self.mon_ref_data = self.mon_ref_data[self.var]
            else:
                 self.mon_ref_data = self.mon_ref_data
            self.mon_ref_data.plot(ax=ax, label=self.ref_label+'-mon', color='black', lw=0.95, zorder=2)
        
        # Plotting annual ensemble data
        if self.ann_dataset_mean is not None:
            if isinstance(self.ann_dataset_mean,xr.Dataset):
                self.ann_dataset_mean = self.ann_dataset_mean[self.var]
            else:
                self.ann_dataset_mean = self.ann_dataset_mean
            if isinstance(self.ann_dataset_std,xr.Dataset):
                self.ann_dataset_std = self.ann_dataset_std[self.var]
            else:
                self.ann_dataset_std = self.ann_dataset_std
            self.ann_dataset_mean.plot(ax=ax, label=self.ensemble_label+'-ann-mean',
                                            color=color_list[2], linestyle='--', zorder=2)
            if self.plot_std:
                ax.fill_between(self.ann_dataset_mean.time,self.ann_dataset_mean - 2.*self.ann_dataset_std,self.ann_dataset_mean +
                                2.*self.ann_dataset_std, facecolor=color_list[2], alpha=0.25, label=self.ensemble_label+'-ann-mean'+r'$\pm2$std', zorder=0)
            if self.plot_ensemble_members:
                for i in range(0,len(self.ann_model_dataset[self.var][:,0])):
                    self.ann_model_dataset[self.var][i, :].plot(ax=ax, color='grey', lw=0.7, linestyle='--', zorder=1)
        
        # Plotting annual reference
        if self.ann_ref_data is not None:
            if isinstance(self.ann_ref_data,xr.Dataset):
                self.ann_ref_data = self.ann_ref_data[self.var]
            else:
                self.ann_ref_data = self.ann_ref_data
            self.ann_ref_data.plot(ax=ax, label=self.ref_label+'-ann', color='black', linestyle='--', lw=0.95, zorder=2)

        ax.set_title(self.plot_title)
        ax.legend(ncol=self.label_ncol, fontsize=self.label_size, framealpha=0)
        
        # Saving plots
        self.logger.info("Saving plots as png and pdf the output folder {self.outputdir}/plots")
        plots_path = os.path.join(self.outputdir, 'plots')
        create_folder(plots_path, self.loglevel)
        # pdf plots
        fig.savefig(os.path.join(plots_path, self.outfile)+'.pdf', bbox_inches='tight', pad_inches=0.1)
        # pdf plots
        fig.savefig(os.path.join(plots_path, self.outfile)+'.png', bbox_inches='tight', pad_inches=0.1)

class EnsembleLatLon():
    """
    A class to compute ensemble mean and standard deviation of a 2D (lon-lat) Dataset.
    Make sure that the dataset has correct lon-lat dimensions.
    """
    def __init__(self, var=None, dataset=None, ensemble_dimension_name="Ensembles", outputdir='./', loglevel='WARNING', **kwargs):
        """
        Args:
            var (str): Variable name.
            dataset: xarray Dataset composed of ensembles 2D lon-lat data, i.e., 
                     the individual Dataset (lon-lat) are concatenated along.
                     a new dimension "Ensemble". This Ensemble name can be changed.
            ensemble_dimension_name="Ensembles" (str): a default name given to the 
                     dimensions along with the individual Datasets were concatenated.
            outputdir (str): String input for output path.
            loglevel (str): Log level. Default is "WARNING".
            **kwargs (dict): dictonary contains options for plots. Defaults values have been set already.
        """
        self.loglevel = loglevel
        self.logger = log_configure(log_level=self.loglevel, log_name='Ensemble')

        self.var = var
        self.dataset = dataset
        self.dataset_mean = None
        self.dataset_std = None
        self.dim = ensemble_dimension_name
        self.outputdir = outputdir + 'Ensemble_LatLon'
        self.outputfile = f'global_2D_map_{self.var}'
        
        self.figure = None
        plot_options = kwargs.get('plot_options',{})
        self.plot_label = plot_options.get('plot_label',True)
        self.plot_std =  plot_options.get('plot_std',True)
        self.figure_size = plot_options.get('figure_size',[15, 15])
        self.dpi = plot_options.get('dpi', 600)
        self.draw_labels = plot_options.get('draw_labels',True)
       
        #TODO: mention is the config file
        # Specific for colorbars is mean and std plots 
        self.vmin_mean = plot_options.get('vmin_mean',None)
        self.vmax_mean = plot_options.get('vmax_mean',None)
        self.vmin_std = plot_options.get('vmin_std',None)
        self.vmax_std = plot_options.get('vmax_std',None)
        
        self.proj = plot_options.get('projection',ccrs.PlateCarree())
        self.transform_first = plot_options.get('transform_first',False)
        self.cyclic_lon = plot_options.get('cyclic_lon',False)
        self.contour = plot_options.get('contour',True)
        self.coastlines = plot_options.get('coastlines',True)
        #
        
        self.units = plot_options.get('units',None)
        if self.units is None:
            self.units = self.dataset[self.var].units
        self.cbar_label = plot_options.get('cbar_label',None)
        if self.cbar_label is None:
            self.cbar_label = self.var+' in ' + self.units
        self.mean_plot_title = plot_options.get('mean_plot_title', f'Map of {self.var} for Ensemble mean')
        self.std_plot_title = plot_options.get('std_plot_title', f'Map of {self.var} for Ensemble standard deviation')

        # TODO: save the ensemble mean and the std values as netcdf files
        # self.netcdf_save = True

    def compute_statistics(self):
        """
        A function to compute the mean and standard devivation of the input dataset
        It is import to make sure that the dim along which the mean is compute is correct.
        The default dim="Ensembles". This can be reassianged with the method "edit_attributes".
        """
        if self.dataset is not None:
            self.dataset_mean = self.dataset.mean(dim=self.dim)
            self.dataset_std = self.dataset.std(dim=self.dim)

    def plot(self):
        """
        This plots the ensemble mean and standard deviation of the ensemble statistics.
        """
        
        self.logger.info('Plotting the ensemble computation')
        create_folder(self.outputdir, self.loglevel)
        outfig = os.path.join(self.outputdir, 'plots')
        self.logger.debug(f"Path to output diectory for plots: {outfig}")
        create_folder(outfig, self.loglevel)

        if self.dataset_mean is not None:
            if isinstance(self.dataset_mean,xr.Dataset):
                self.dataset_mean = self.dataset_mean[self.var]
            else:
                self.dataset_mean = self.dataset_mean
            if self.vmin_mean is None:
                self.vmin_mean = self.dataset_mean.values.min()
            if self.vmax_mean is None:
                self.vmax_mean = self.dataset_mean.values.max()
            fig, ax = plot_single_map(self.dataset_mean, proj=self.proj, contour=self.contour, cyclic_lon=self.cyclic_lon, coastlines=self.coastlines, transform_first=self.transform_first, return_fig=True, title=self.mean_plot_title, vmin=self.vmin_mean, vmax=self.vmax_mean)
            ax.set_xlabel("Longitude")
            ax.set_ylabel("Latitude")
            self.logger.debug(f"Saving 2D map of mean to {outfig}")
            # 2D mean plot in pdf
            fig.savefig(os.path.join(outfig, self.var+'_LatLon_mean.pdf'),bbox_inches='tight', pad_inches=0.1, dpi=self.dpi)
            # 2D mean plots in png
            fig.savefig(os.path.join(outfig, self.var+'_LatLon_mean.png'),bbox_inches='tight', pad_inches=0.1, dpi=self.dpi)

        if self.dataset_std is not None:
            if isinstance(self.dataset_std,xr.Dataset):
                self.dataset_std = self.dataset_std[self.var]
            else:
                self.dataset_std = self.dataset_std
            if self.vmin_std is None:
                self.vmin_std = self.dataset_std.values.min()
            if self.vmax_std is None:
                self.vmax_std = self.dataset_std.values.max()
            fig, ax = plot_single_map(self.dataset_std, proj=self.proj, contour=self.contour, cyclic_lon=self.cyclic_lon, coastlines=self.coastlines, transform_first=self.transform_first, return_fig=True, title=self.std_plot_title, vmin=self.vmin_std, vmax=self.vmax_std)
            ax.set_xlabel("Longitude")
            ax.set_ylabel("Latitude")
            self.logger.debug(f"Saving 2D map of STD to {outfig}")
            # 2D STD plot in pdf
            fig.savefig(os.path.join(outfig, self.var+'_LatLon_STD.pdf'),bbox_inches='tight', pad_inches=0.1, dpi=self.dpi)
            # 2D STD plots in png
            fig.savefig(os.path.join(outfig, self.var+'_LatLon_STD.png'),bbox_inches='tight', pad_inches=0.1, dpi=self.dpi)

class EnsembleZonal():
    """
    A class to compute ensemble mean and standard deviation of the Zonal averages
    Make sure that the dataset has correct lev-lat dimensions.
    """
    def __init__(self, var=None, dataset=None, ensemble_dimension_name="Ensembles", outputdir='./', loglevel='WARNING', **kwargs):
        """
        Args:
            var (str): Variable name.
            dataset: xarray Dataset composed of ensembles 2D Zonal data, i.e., 
                     the individual Dataset (lev-lat) are concatenated along.
                     a new dimension "Ensemble". This Ensemble name can be changed.
            ensemble_dimension_name="Ensembles" (str): a default name given to the 
                     dimensions along with the individual Datasets were concatenated.
            loglevel (str): Log level. Default is "WARNING".
            **kwargs (dict): dictonary contains options for plots. Defaults values have been set already.
        """
        self.loglevel = loglevel
        self.logger = log_configure(log_level=self.loglevel, log_name='Ensembles')

        self.var = var
        self.dataset = dataset
        self.dim = ensemble_dimension_name
        self.dataset_mean = None
        self.dataset_std = None

        self.outputdir = outputdir + 'Ensemble_Zonal'
        self.outputfile = f'global_Zonal_plot_{var}'

        self.figure = None
        plot_options = kwargs.get('plot_options',{})
        self.plot_label = plot_options.get('plot_label',True)
        self.plot_std =  plot_options.get('plot_std',True)
        self.figure_size = plot_options.get('figure_size',[15, 15])
        self.units = plot_options.get('units',None)
        self.dpi = plot_options.get('dpi', 300)
        if self.units is None:
            self.units = self.dataset[self.var].units
        self.cbar_label = plot_options.get('cbar_label',None)
        if self.cbar_label is None:
            self.cbar_label = self.var+' in ' + self.units
        self.mean_plot_title = plot_options.get('mean_plot_title', f'Ensemble mean zonal average of {self.var}')
        self.std_plot_title = plot_options.get('std_plot_title', f'Ensemble standard deviation of zonal average of {self.var}')

    def compute_statistics(self):
        """
        A function to compute the mean and standard devivation of the input dataset
        It is import to make sure that the dim along which the mean is compute is correct.
        The default dim="Ensembles". This can be reassianged with the method "edit_attributes".
        """
        if self.dataset != None:
            self.dataset_mean = self.dataset.mean(dim=self.dim)
            self.dataset_std = self.dataset.std(dim=self.dim)

    def plot(self):
        """
        This plots the ensemble mean and standard deviation of the ensemble statistics.
        To edit the default settings please call the method "edit_attributes"
        """
        self.logger.info('Plotting the ensemble computation of Zonal-averages as mean and STD in Lev-Lon of var {self.var}')
        create_folder(self.outputdir, self.loglevel)
        outfig = os.path.join(self.outputdir, 'plots')
        self.logger.debug(f"Path to output diectory for plots: {outfig}")
        create_folder(outfig, self.loglevel)

        # projection = ccrs.PlateCarree()
        var = self.var
        if self.dataset_mean is not None:
            if isinstance(self.dataset_mean,xr.Dataset):
                self.dataset_mean = self.dataset_mean[self.var]
            else:
                self.dataset_mean = self.dataset_mean
            self.logger.info("Plotting ensemble-mean Zonal-average") 
            fig = plt.figure(figsize=(self.figure_size[0], self.figure_size[1]))
            ax = fig.add_subplot(1,1,1)
            im = ax.contourf(self.dataset_mean.lat,self.dataset_mean.lev,self.dataset_mean,cmap='RdBu_r', levels=20, extend='both')
            ax.set_ylim((5500, 0))
            ax.set_ylabel("Depth (in m)", fontsize=9)
            ax.set_xlabel("Latitude (in deg North)", fontsize=9)
            ax.set_facecolor('grey')
            ax.set_title(self.mean_plot_title)
            cbar = fig.colorbar(im, ax=ax, shrink=0.9, extend='both')
            cbar.set_label(self.cbar_label)
            self.logger.debug(f"Saving Lev-Lon Zonal-average ensemble-mean as pdf and png to {outfig}")
            # Lev-Lon Zonal mean plot in pdf
            fig.savefig(os.path.join(outfig, self.var+'_LevLon_mean.pdf'),bbox_inches='tight', pad_inches=0.1, dpi=self.dpi)
            # Lev-Lon Zonal mean plot in png
            fig.savefig(os.path.join(outfig, self.var+'_LevLon_mean.png'),bbox_inches='tight', pad_inches=0.1, dpi=self.dpi)

        if self.dataset_std is not None:
            if isinstance(self.dataset_std,xr.Dataset):
                self.dataset_std = self.dataset_std[self.var]
            else:
                self.dataset_std = self.dataset_std
            self.logger.info("Plotting ensemble-STD Zonal-average") 
            fig = plt.figure(figsize=(self.figure_size[0], self.figure_size[1]))
            ax = fig.add_subplot(1,1,1)
            im = ax.contourf(self.dataset_std.lat,self.dataset_std.lev,self.dataset_std,cmap='OrRd', levels=20, extend='both')
            ax.set_ylim((5500, 0))
            ax.set_ylabel("Depth (in m)", fontsize=9)
            ax.set_xlabel("Latitude (in deg North)", fontsize=9)
            ax.set_facecolor('grey')
            ax.set_title(self.std_plot_title)
            cbar = fig.colorbar(im, ax=ax,shrink=0.9, extend='both')
            cbar.set_label(self.cbar_label)
            self.logger.debug(f"Saving Lev-Lon Zonal-average ensemble-STD as pdf and png to {outfig}")
            # Lev-Lon Zonal STD plot in pdf
            fig.savefig(os.path.join(outfig, self.var+'_LevLon_STD.pdf'),bbox_inches='tight', pad_inches=0.1, dpi=self.dpi)
            # Lev-Lon Zonal STD plot in png
            fig.savefig(os.path.join(outfig, self.var+'_LevLon_STD.png'),bbox_inches='tight', pad_inches=0.1, dpi=self.dpi)


