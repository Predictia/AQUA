import os
import gc

import xarray as xr
from aqua import Reader
from aqua.logger import log_configure
from aqua.exceptions import NoObservationError, NoDataError
from aqua.util import create_folder
from aqua.util import add_pdf_metadata, time_to_string
from aqua.graphics import plot_timeseries
import matplotlib.pyplot as plt
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
                 ensemble_dimension_name="Ensembles",
                 loglevel='WARNING'):
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
            loglevel (str): Log level. Default is "WARNING".
        """
        self.loglevel = loglevel
        self.logger = log_configure(log_level=self.loglevel, log_name='Ensemble Timeseries')
        self.var = var
        self.mon_model_dataset = mon_model_dataset
        self.ann_model_dataset = ann_model_dataset
        self.mon_ref_data = mon_ref_data
        self.ann_ref_data = ann_ref_data

        self.plot_std = True
        self.plot_label = True

        self.outdir = None
        self.outfile = None

        self.mon_dataset_mean = None
        self.mon_dataset_std = None

        self.ann_dataset_mean = None
        self.ann_dataset_std = None

        self.plot_std = True
        self.plot_ensemble_members = True
        self.plot_ref = True
        self.figure_size = [10, 5]
        self.outfile = None
        self.outdir = './'
        self.label_size = 7.5
        self.ensemble_label = 'Ensemble'
        self.ref_label = 'ERA5'
        self.plot_title = None
        self.dim = ensemble_dimension_name
        self.label_ncol = 4
        self.pdf_save = True
        if self.pdf_save is False:
            self.logger.info("Figure will not be saved")

    def ensemble_mean(self, dataset):
        return dataset[self.var].mean(dim=self.dim)

    def ensemble_std(self, dataset):
        return dataset[self.var].std(dim=self.dim)

    def compute(self):
        """
        A function to compute the mean and standard devivation of the input dataset
        It is import to make sure that the dim along which the mean is compute is correct.
        The default dim="Ensembles". This can be reassianged with the method "edit_attributes".
        """
        if self.mon_model_dataset != None:
            self.mon_dataset_mean = self.ensemble_mean(self.mon_model_dataset)
        if self.ann_model_dataset != None:
            self.ann_dataset_mean = self.ensemble_mean(self.ann_model_dataset)

        if self.mon_model_dataset != None:
            self.mon_dataset_std = self.ensemble_std(self.mon_model_dataset)
        if self.ann_model_dataset != None:
            self.ann_dataset_std = self.ensemble_std(self.ann_model_dataset)

    def edit_attributes(self, **kwargs):
        """
        This method helps edit the default attributes. 
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                print(f"Attribute '{key}' does not exist.")

    def plot(self):
        """
        This plots the ensemble mean and standard deviation of the ensemble statistics.
        To edit the default settings please call the method "edit_attributes"
        """
        self.logger.info('Plotting the ensemble timeseries')
        var = self.var[0]  # Only one variable can be plotted at a time
        plt.rcParams["figure.figsize"] = (self.figure_size[0], self.figure_size[1])
        fig, ax = plt.subplots(1, 1)
        color_list = ["#1898e0", "#8bcd45", "#f89e13", "#d24493", "#00b2ed", "#dbe622",
                      "#fb4c27", "#8f57bf", "#00bb62", "#f9c410", "#fb4865", "#645ccc"]

        # Plotting monthly ensemble data
        if self.mon_dataset_mean != None:
            self.mon_dataset_mean[var].plot(ax=ax, label=self.ensemble_label+'-mon-mean', color=color_list[0], zorder=2)
            if self.plot_std:
                ax.fill_between(self.mon_dataset_mean.time, self.mon_dataset_mean[var] - 2.*self.mon_dataset_std[var], self.mon_dataset_mean[var] +
                                2.*self.mon_dataset_std[var], facecolor=color_list[0], alpha=0.25, label=self.ensemble_label+'-mon-mean'+r'$\pm2$std', zorder=0)
            if self.plot_ensemble_members:
                for i in range(len(self.mon_model_dataset)):
                    self.mon_model_dataset[var][i, :].plot(ax=ax, color='grey', lw=0.7, zorder=1)

        # Plotting monthy reference
        if self.mon_ref_data != None:
            self.mon_ref_data[var].plot(ax=ax, label=self.ref_label+'-mon', color='black', lw=0.95, zorder=2)

        # Plotting annual ensemble data
        if self.ann_dataset_mean != None:
            self.ann_dataset_mean[var].plot(ax=ax, label=self.ensemble_label+'-ann-mean',
                                            color=color_list[2], linestyle='--', zorder=2)
            if self.plot_std:
                ax.fill_between(self.ann_dataset_mean.time, self.ann_dataset_mean[var] - 2.*self.ann_dataset_std[var], self.ann_dataset_mean[var] +
                                2.*self.ann_dataset_std[var], facecolor=color_list[2], alpha=0.25, label=self.ensemble_label+'-ann-mean'+r'$\pm2$std', zorder=0)
            if self.plot_ensemble_members:
                for i in range(len(self.ann_model_dataset)):
                    self.ann_model_dataset[var][i, :].plot(ax=ax, color='grey', lw=0.7, linestyle='--', zorder=1)

        # Plotting annual reference
        if self.ann_ref_data != None:
            self.ann_ref_data[var].plot(ax=ax, label=self.ref_label+'-ann', color='black', linestyle='--', lw=0.95, zorder=2)
        ax.set_title(self.plot_title)
        ax.legend(ncol=self.label_ncol, fontsize=self.label_size, framealpha=0)

        # Save PDF
        if self.pdf_save:
            self.save_pdf(fig, self.ref_label)

    def save_pdf(self, fig, ref_label):
        """
        This method creates the pdf of the output plots and is used inside the plot function
        """
        self.logger.info("Saving figure to pdf")
        outfig = os.path.join(self.outdir, 'pdf')
        self.logger.debug(f"Saving figure to {outfig}")
        create_folder(outfig, self.loglevel)
        if self.outfile is None:
            self.outfile = f'multimodel_global_time_series_timeseries_{self.var}'
        self.outfile += '.pdf'
        self.logger.debug(f"Outfile: {self.outfile}")
        fig.savefig(os.path.join(outfig, self.outfile))

    def run(self):
        self.compute()
        self.edit_attributes()
        self.plot()


