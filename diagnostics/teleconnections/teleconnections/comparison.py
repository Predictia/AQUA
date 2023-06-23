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

