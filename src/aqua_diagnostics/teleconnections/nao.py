from .base import BaseMixin


class Nao(BaseMixin):
    """
    North Atlantic Oscillation (NAO) index calculation class.
    This class is used to calculate the NAO index from a given dataset.
    It inherits from the BaseMixin class and implements the necessary methods
    to calculate the NAO index.
    """
    def __init__(self, catalog: str = None, model: str = None,
                 exp: str = None, source: str = None,
                 regrid: str = None,
                 startdate: str = None, enddate: str = None,
                 loglevel: str = 'WARNING'):
        super().__init__(catalog=catalog, model=model, exp=exp, source=source,
                         regrid=regrid, startdate=startdate, enddate=enddate,
                         loglevel=loglevel)