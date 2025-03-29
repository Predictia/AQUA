import matplotlib.pyplot as plt

from aqua.logger import log_configure
from aqua.util import evaluate_colorbar_limits, to_list
from .styles import ConfigStyle


def plot_gregory_monthly(t2m_monthly_data, net_toa_monthly_data,
                         t2m_monthly_ref, net_toa_monthly_ref,
                         fig: plt.Figure = None, ax: plt.Axes = None,
                         set_axis_limits: bool = True, legend: bool = True,
                         labels=None, style: str = None,
                         loglevel: str = 'WARNING'):

    logger = log_configure(loglevel, 'plot_gregory_monthly')
    ConfigStyle(style=style, loglevel=loglevel)

    labels = to_list(labels) if labels else [None for _ in range(len(t2m_monthly_data))]

    if fig is None and ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(6, 6))

    if set_axis_limits:
        # We set a fixed x and y range but then we expand it if data
        # goes beyond the limits
        t2m_list = to_list(t2m_monthly_data) + to_list(t2m_monthly_ref)
        t2m_min, t2m_max = evaluate_colorbar_limits(t2m_list, sym=False)
        t2m_min = min(t2m_min, 10.5)
        t2m_max = max(t2m_max, 16)

        net_toa_list = to_list(net_toa_monthly_data) + to_list(net_toa_monthly_ref)
        toa_min, toa_max = evaluate_colorbar_limits(net_toa_list, sym=False)
        toa_min = min(toa_min, -11.5)
        toa_max = max(toa_max, 11.5)

        ax.set_xlim(t2m_min+0.5, t2m_max-0.5)
        ax.set_ylim(toa_min+0.5, toa_max-0.5)

        logger.debug(f"Monthly x-axis limits: {t2m_min} to {t2m_max}")
        logger.debug(f"Monthly y-axis limits: {toa_min} to {toa_max}")

    ax.set_title('Monthly Gregory Plot')
    ax.set_xlabel('2 m Temperature [°C]')
    ax.set_ylabel("Net radiation TOA [W/m^2]")
    ax.axhline(0, color="k")
    ax.grid(True)

    for i, (t2m_monthly, net_toa_monthly) in enumerate(zip(t2m_monthly_data, net_toa_monthly_data)):
        ax.plot(t2m_monthly, net_toa_monthly, label=labels[i], marker='o')

    t2m_ref = t2m_monthly_ref.groupby('time.month').mean(dim='time')
    net_toa_ref = net_toa_monthly_ref.groupby('time.month').mean(dim='time')
    ax.plot(t2m_ref, net_toa_ref, label='Reference', marker='o', color='black')

    if legend:
        ax.legend()

    return fig, ax
