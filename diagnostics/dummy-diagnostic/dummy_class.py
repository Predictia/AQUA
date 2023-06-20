"""Dummy diagnostic for testing purposes"""

from aqua import catalogue


class DummyDiagnostic():
    """Dummy diagnostic class"""

    def __init__(self, option=None, configdir=None):
        """
        The DummyDiagnostic constructor.

        Parameters
        ----------
        option : str
            The option to be passed to the diagnostic.
        configdir : str
            The configuration directory.

        Returns
        -------
        None.

        """

        self.option = option
        self.configdir = configdir

    def run(self):
        """
        The run method.

        Returns
        -------
        None.

        """

        cat = catalogue(configdir=self.configdir)
        print(cat)
