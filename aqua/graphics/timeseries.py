"""
Function to plot timeseries and reference data,
both with monthly and annual aggregation options
"""
import matplotlib.pyplot as plt


def plot_timeseries(monthly_data=None,
                    annual_data=None,
                    ref_monthly_data=None,
                    ref_annual_data=None,
                    std_monthly_data=None,
                    std_annual_data=None,
                    data_labels: list = None,
                    ref_label: str = None,
                    **kwargs):
    """
    monthly_data and annual_data are list of xr.DataArray
    that are plot as timeseries together with their reference
    data and standard deviation.

    Arguments:
        monthly_data (list of xr.DataArray): monthly data to plot
        annual_data (list of xr.DataArray): annual data to plot
        ref_monthly_data (xr.DataArray): reference monthly data to plot
        ref_annual_data (xr.DataArray): reference annual data to plot
        std_monthly_data (xr.DataArray): standard deviation of the reference monthly data
        std_annual_data (xr.DataArray): standard deviation of the reference annual data
        data_labels (list of str): labels for the data
        ref_label (str): label for the reference data

    Keyword Arguments:
        figsize (tuple): size of the figure
        title (str): title of the plot

    Returns:
        fig, ax (tuple): tuple containing the figure and axis objects
    """
    fig_size = kwargs.get('figsize', (10, 5))
    fig, ax = plt.subplots(1, 1, figsize=fig_size)

    color_list = ["#1898e0", "#8bcd45", "#f89e13", "#d24493",
                  "#00b2ed", "#dbe622", "#fb4c27", "#8f57bf",
                  "#00bb62", "#f9c410", "#fb4865", "#645ccc"]

    for i in range(len(monthly_data)):
        color = color_list[i]
        if monthly_data:
            mon_data = monthly_data[i]
            if data_labels:
                label = data_labels[i]
                label += ' monthly'
            mon_data.plot(ax=ax, label=label, color=color)
        if annual_data:
            ann_data = annual_data[i]
            if data_labels:
                label = data_labels[i]
                label += ' annual'
            ann_data.plot(ax=ax, label=label, color=color, linestyle='--')

    if ref_monthly_data is not None:
        ref_monthly_data.plot(ax=ax, label=ref_label + ' monthly', color='grey')
        if std_monthly_data is not None:
            std_monthly_data.compute()
            ax.fill_between(ref_monthly_data.time,
                            ref_monthly_data - 2.*std_monthly_data.sel(month=ref_monthly_data["time.month"]),
                            ref_monthly_data + 2.*std_monthly_data.sel(month=ref_monthly_data["time.month"]),
                            facecolor='grey', alpha=0.3)

    if ref_annual_data is not None:
        ref_annual_data.plot(ax=ax, label=ref_label + ' annual', color='black', linestyle='--')
        if std_annual_data is not None:
            std_annual_data.compute()
            ax.fill_between(ref_annual_data.time,
                            ref_annual_data - 2.*std_annual_data,
                            ref_annual_data + 2.*std_annual_data,
                            facecolor='black', alpha=0.3)

    ax.legend(fontsize='small')

    title = kwargs.get('title', None)
    if title:
        ax.set_title(title)

    return fig, ax
