import matplotlib.pyplot as plt
from aqua.graphics import indexes_plot
from .base import PlotBaseMixin


class PlotENSO(PlotBaseMixin):

    def __init__(self, loglevel: str = 'WARNING'):
        super().__init__(loglevel=loglevel)

    def plot_index(self, indexes: list, thresh: float = 0.5):
        
        fig, axs = indexes_plot(indexes=indexes, thresh=thresh)

        if isinstance(axs, plt.Axes):
            axs = [axs]

        for i in range(len(axs)):
            ax = axs[i]

            ax.set_ylim(min(ax.get_ylim()[0], -2.1), max(ax.get_ylim()[1], 2.1))

            textoffset = 0.08

            ax.text(
                x=ax.get_xlim()[1],
                y=2. + textoffset,
                s='El Niño',
                color='red',
                fontsize=10,
                ha='right',
                va='center'
            )

            ax.text(
                x=ax.get_xlim()[1],
                y=-2. + textoffset,
                s='La Niña',
                color='blue',
                fontsize=10,
                ha='right',
                va='center'
            )
