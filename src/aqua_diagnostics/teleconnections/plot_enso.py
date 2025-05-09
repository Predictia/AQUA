import matplotlib.pyplot as plt
from aqua.graphics import indexes_plot
from .base import PlotBaseMixin


class PlotENSO(PlotBaseMixin):

    def __init__(self, indexes=None, ref_indexes=None, outputdir: str = './', rebuild: bool = True,
                 loglevel: str = 'WARNING'):
        """
        Plot the ENSO products.

        Args:
            indexes (list): List of indexes to plot.
            ref_indexes (list): List of reference indexes to plot.
            outputdir (str): Directory to save the plots. Default is './'.
            rebuild (bool): If True, rebuild the plots. Default is True.
            loglevel (str): Log level for the logger. Default is 'WARNING'.
        """
        super().__init__(indexes=indexes, ref_indexes=ref_indexes, diagnostic='enso',
                         outputdir=outputdir, rebuild=rebuild, loglevel=loglevel)

    def plot_index(self, thresh: float = 0.5):

        # Join the indexes in a single list
        indexes = self.indexes + self.ref_indexes

        labels = super().set_labels()
        
        fig, axs = indexes_plot(indexes=indexes, thresh=thresh, suptitle='ENSO3.4 index',
                                ylabel='ENSO3.4 index', labels=labels, loglevel=self.loglevel)

        if isinstance(axs, plt.Axes):
            axs = [axs]

        # Indexes customization for ENSO only
        for i in range(len(axs)):
            ax = axs[i]

            ylim = 2.3
            ax.set_ylim(min(ax.get_ylim()[0], -ylim), max(ax.get_ylim()[1], ylim))

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

        return fig, axs

    def set_index_description(self):
        return super().set_index_description(index_name='ENSO3.4')