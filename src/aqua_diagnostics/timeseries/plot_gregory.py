import matplotlib.pyplot as plt
from aqua.graphics import ConfigStyle, plot_gregory_monthly, plot_gregory_annual
from aqua.logger import log_configure
from aqua.util import to_list
from .base import PlotBaseMixin


class PlotGregory(PlotBaseMixin):
    def __init__(self, t2m_monthly_data=None, net_toa_monthly_data=None,
                 t2m_annual_data=None, net_toa_annual_data=None,
                 t2m_monthly_ref=None, net_toa_monthly_ref=None,
                 t2m_annual_ref=None, net_toa_annual_ref=None,
                 t2m_annual_std=None, net_toa_annual_std=None,
                 loglevel: str = 'WARNING'):
        """
        Initialize the class with the data to be plotted

        Args:
            t2m_monthly_data: List of monthly 2m temperature data
            net_toa_monthly_data: List of monthly net toa data
            t2m_annual_data: List of annual 2m temperature data
            net_toa_annual_data: List of annual net toa data
            t2m_monthy_ref: Monthly reference 2m temperature data
            net_toa_monthy_ref: Monthly reference net toa data
            t2m_annual_ref: Aannual reference 2m temperature data
            net_toa_annual_ref: Annual reference net toa data
            t2m_annual_std: Annual standard deviation of 2m temperature data
            net_toa_annual_std: Annual standard deviation of net toa data
            loglevel: Logging level. Default is 'WARNING'
        """
        super().__init__(loglevel=loglevel)
        self.logger = log_configure(self.loglevel, 'PlotGregory')

        self.monthly_data = {'t2m': to_list(t2m_monthly_data), 'net_toa': to_list(net_toa_monthly_data)}
        self.annual_data = {'t2m': to_list(t2m_annual_data), 'net_toa': to_list(net_toa_annual_data)}
        self.monthly_ref = {'t2m': t2m_monthly_ref, 'net_toa': net_toa_monthly_ref}
        self.annual_ref = {'t2m': t2m_annual_ref, 'net_toa': net_toa_annual_ref}
        self.annual_std = {'t2m': t2m_annual_std, 'net_toa': net_toa_annual_std}

        self.data_dict = {'monthly': self.monthly_data, 'annual': self.annual_data}
        self.ref_dict = {'monthly': self.monthly_ref, 'annual': self.annual_ref}
        self.std_dict = {'monthly': None, 'annual': self.annual_std}

        self.get_data_info()

    def plot(self, freq=['monthly', 'annual'], title: str = None, style: str = 'aqua'):
        """
        Plot the data

        Args:
            freq: List of frequency for plotting. Default is ['monthly', 'annual']
            title: Title of the plot. Default is None
            style: Style of the plot. Default is 'aqua'
        """
        ConfigStyle(style=style)
        ax_monthly = None
        ax_annual = None

        freq_dict = {'monthly': ax_monthly, 'annual': ax_annual}

        if 'monthly' in freq and 'annual' in freq:
            fig, (ax_monthly, ax_annual) = plt.subplots(1, 2, figsize=(12, 6))
        elif 'monthly' in freq and 'annual' not in freq:
            fig, ax_monthly = plt.subplots(1, 1, figsize=(6, 6))
        elif 'annual' in freq and 'monthly' not in freq:
            fig, ax_annual = plt.subplots(1, 1, figsize=(6, 6))
        else:
            raise ValueError('Invalid frequency for plotting, allowed values are "monthly" and "annual"')

        if ax_monthly:
            fig, ax_monthly = self.plot_monthly(fig, ax_monthly)
        if ax_annual:
            fig, ax_annual = self.plot_annual(fig, ax_annual)

        # We extract the handles and labels from each axis
        # since the labels are defined in the plotting function
        handles, labels = [], []
        for f in freq:
            ax = freq_dict[f]
            if ax is not None:
                h_for, l_for = ax.get_legend_handles_labels()
                handles.extend(h_for)
                labels.extend(l_for)

        # Create a single legend at the bottom
        fig.legend(handles, labels, loc="lower center", ncol=2)

        # Adjust layout to make space
        fig.subplots_adjust(bottom=0.2)

        if title:
            fig.suptitle(title)

        return fig

    def set_title(self):
        title = 'Gregory Plot '
        return title

    def plot_monthly(self, fig, ax):
        fig, ax = plot_gregory_monthly(t2m_monthly_data=self.monthly_data['t2m'],
                                       net_toa_monthly_data=self.monthly_data['net_toa'],
                                       t2m_monthly_ref=self.monthly_ref['t2m'],
                                       net_toa_monthly_ref=self.monthly_ref['net_toa'],
                                       fig=fig, ax=ax, loglevel=self.loglevel)
        return fig, ax

    def plot_annual(self, fig, ax):
        fig, ax = plot_gregory_annual(t2m_annual_data=self.annual_data['t2m'],
                                      net_toa_annual_data=self.annual_data['net_toa'],
                                      t2m_annual_ref=self.annual_ref['t2m'],
                                      net_toa_annual_ref=self.annual_ref['net_toa'],
                                      t2m_std=self.std_dict['annual']['t2m'],
                                      net_toa_std=self.std_dict['annual']['net_toa'],
                                      fig=fig, ax=ax, loglevel=self.loglevel)
        return fig, ax

    def get_data_info(self):
        """
        We extract the data needed for labels, description etc
        from the data arrays attributes.

        The attributes are:
        - AQUA_catalog
        - AQUA_model
        - AQUA_exp
        """
        for var in self.data_dict.values():
            for data in var.values():
                self.catalogs = [d.AQUA_catalog for d in data]
                self.models = [d.AQUA_model for d in data]
                self.exps = [d.AQUA_exp for d in data]

        if self.ref_dict['monthly']['t2m'] is not None:
            t2m_catalog = self.ref_dict['monthly']['t2m'].AQUA_catalog
            t2m_model = self.ref_dict['monthly']['t2m'].AQUA_model
            t2m_exp = self.ref_dict['monthly']['t2m'].AQUA_exp
        elif self.ref_dict['annual']['t2m'] is not None:
            t2m_catalog = self.ref_dict['annual']['t2m'].AQUA_catalog
            t2m_model = self.ref_dict['annual']['t2m'].AQUA_model
            t2m_exp = self.ref_dict['annual']['t2m'].AQUA_exp
        else:
            t2m_catalog = None
            t2m_model = None
            t2m_exp = None

        if self.ref_dict['monthly']['net_toa'] is not None:
            net_toa_catalog = self.ref_dict['monthly']['net_toa'].AQUA_catalog
            net_toa_model = self.ref_dict['monthly']['net_toa'].AQUA_model
            net_toa_exp = self.ref_dict['monthly']['net_toa'].AQUA_exp
        elif self.ref_dict['annual']['net_toa'] is not None:
            net_toa_catalog = self.ref_dict['annual']['net_toa'].AQUA_catalog
            net_toa_model = self.ref_dict['annual']['net_toa'].AQUA_model
            net_toa_exp = self.ref_dict['annual']['net_toa'].AQUA_exp
        else:
            net_toa_catalog = None
            net_toa_model = None
            net_toa_exp = None

        self.ref_catalogs = {'t2m': t2m_catalog, 'net_toa': net_toa_catalog}
        self.ref_models = {'t2m': t2m_model, 'net_toa': net_toa_model}
        self.ref_exps = {'t2m': t2m_exp, 'net_toa': net_toa_exp}
