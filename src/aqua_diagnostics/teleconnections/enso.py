from aqua.exceptions import NotEnoughDataError
from aqua.logger import log_configure
from aqua.util.sci_util import _lon_180_to_360
from .base import BaseMixin


class ENSO(BaseMixin):
    """
    Class for calculating the El Niño Southern Oscillation (ENSO) index.
    This class is used to calculate the ENSO index from a given dataset.
    It inherits from the BaseMixin class and implements the necessary methods
    to calculate the ENSO index.
    """
    def __init__(self, catalog: str = None, model: str = None,
                 exp: str = None, source: str = None,
                 regrid: str = None,
                 startdate: str = None, enddate: str = None,
                 configdir: str = None,
                 interface: str = 'teleconnections-destine',
                 loglevel: str = 'WARNING'):
        super().__init__(telecname='ENSO', catalog=catalog, model=model, exp=exp, source=source,
                         regrid=regrid, startdate=startdate, enddate=enddate,
                         configdir=configdir, interface=interface,
                         loglevel=loglevel)
        self.logger = log_configure(log_name='ENSO', log_level=loglevel)

        self.var = self.interface.get('field')

    def retrieve(self):
        # Assign self.data, self.reader, self.catalog
        super().retrieve(var=self.var)

        self.reader.timmean(self.data, freq='MS')
    
    def compute_index(self, months_window: int = 3,
                       rebuild: bool = False):
        """"
        Evaluate station based index for a teleconnection.
        Field data must be monthly gridded data.

        Args:
            months_window (int, opt): months for rolling average, default is 3
            rebuild (bool, opt): if True, the index is recalculated, default is False
        """
        
