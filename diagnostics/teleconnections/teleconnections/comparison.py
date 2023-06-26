"""Module to compare different experiments telecoonection indices"""
from aqua.logger import log_configure

from teleconnections.tc_class import Teleconnection


class TeleconnectionComparison():
    """Class to compare teleconnections of different models."""

    def __init__(self, telecname: str,
                 models: list, exps: list, sources: list,
                 savefig=False, outputfig=None,
                 savefile=False, outputdir=None,
                 loglevel: str = 'WARNING'):
        """Initialize teleconnection comparison object."""

        # Configure logger
        self.loglevel = loglevel
        self.logger = log_configure(self.loglevel, 'TeleconnectionComparison')

        avail_telec = ['NAO', 'ENSO']
        if telecname in avail_telec:
            self.telecname = telecname
        else:
            raise ValueError('telecname must be one of {}'.format(avail_telec))
        self.logger.debug('Teleconnection: {}'.format(self.telecname))

        self.models = models
        self.exps = exps
        self.sources = sources
        if len(self.models) != len(self.exps) != len(self.sources):
            raise ValueError('models, exps and sources must have the same length')
        for i in range(len(self.models)):
            self.logger.debug('Model: {}/{}/{}'.format(self.models[i], self.exps[i], self.sources[i]))

        self.teleconnection = []
        for i in range(len(self.models)):
            self.logger.debug('Open dataset: {}/{}/{}'.format(self.models[i], self.exps[i], self.sources[i]))
            self.teleconnection.append(Teleconnection(model=self.models[i],
                                                      exp=self.exps[i],
                                                      source=self.sources[i],
                                                      telecname=self.telecname,
                                                      savefig=savefig,
                                                      outputfig=outputfig,
                                                      savefile=savefile,
                                                      outputdir=outputdir,
                                                      loglevel=self.loglevel))

    def index_comparison(self):
        """Compare teleconnection indices."""
        for i in range(len(self.models)):
            self.teleconnection[i].evaluate_index()
            self.logger.debug('Teleconnection index for {}/{}/{}: {}'.format(self.models[i],
                                                                            self.exps[i],
                                                                            self.sources[i],
                                                                            self.teleconnection[i].index))

    def plot_comparison(self):
        """Plot teleconnection indices."""
        # Here we need to use the plot function from the teleconnection func
        # I need to modify the plot function to accept a list of teleconnection objects
        pass

    def regression(self):
        """Perform regression."""
        # Here we need to use the plot function from the teleconnection func
        # I need to modify the plot function to accept a list of teleconnection objects
        pass

    def correlation(self):
        """Perform correlation."""
        # Here we need to use the plot function from the teleconnection func
        # I need to modify the plot function to accept a list of teleconnection objects
        pass

    def NCAR_comparison(self):
        """Compare teleconnection indices with NCAR."""
        # Here we need to use the plot function from the notebook
        # I need to modify the plot function to accept a list of teleconnection objects
        # and to make it different for each teleconnection

        pass
