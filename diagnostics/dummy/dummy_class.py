"""Dummy diagnostic for testing purposes"""
import xarray as xr

from aqua.logger import log_configure
from aqua.reader import Reader


class DummyDiagnostic():
    """Dummy diagnostic class"""
    def __init__(self, model=None, exp=None, source=None,
                 configdir=None, regrid=None,
                 timemean=False, freq=None,
                 savefig=False, outputfig=None,
                 savefile=False, outputdir=None,
                 filename=None, loglevel='WARNING'):
        """
        The DummyDiagnostic constructor.
        The init method is used to initialize the class.
        It is called when the class is instantiated.
        You can pass arguments to the class when you instantiate it.
        Please adapt the arguments to your needs.
        Take care of the default values. They should be the default that
        you want to use in your diagnostic.
        User should be able to run the default diagnostic setup having only
        to specify the model, experiment and source plus some directory
        or name specifications about where to store the outputs.
        Feel free to add more arguments if you need them.
        Feel freecas well to remove arguments if you do not need them,
        for instance if you do not need to regrid or to compute the time mean.
        Please keep the loglevel argument. It is used to configure the logger
        and it's preferable to have it in the init method rather that using
        print statements.

        Args:
            model (str):          the model name to be used by the Reader class.
                                  Default is None.
            exp (str):            the experiment name to be used by the Reader class.
                                  Default is None.
            source (str):         the source name to be used by the Reader class.
                                  Default is None.
            configdir (str):      the path to the directory containing the config files.
                                  Default is None. Please change it to the path of your config files,
                                  if you have any or if there is a clear config directory.
            regrid (str, opt):    whether to regrid the data or not.
                                  Default is None.
                                  Please change it to the default value that you want to use,
                                  considering that it will be the one used by the Reader class
                                  if the user does not specify it.
            timemean (bool,opt):  whether to compute the time mean or not.
                                  Default is False.
                                  Please change it to the default value that you want to use,
                                  considering that it will be the one used by the Reader class
                                  if the user does not specify it.
                                  Consider that time mean can be a very long operation.
                                  If you want to compute the time mean, please consider
                                  making use of the parallelization capabilities of xarray.
                                  You can find more examples in the lra or gribber framework code.
            freq (str, opt):      the frequency of the data temporal aggregation.
                                  Default is None.
                                  Please change it to the default value that you want to use,
                                  considering that it will be the one used by the Reader class
                                  if the user does not specify it.
                                  Consider also that this value will be used only if timemean is True.
            savefig (bool, opt):  whether to save the figures or not.
                                  Default is False to not produce figures files in the notebooks.
                                  Consider that it may be suggested to have it True by default
                                  when running the diagnostic from the command line.
            outputfig (str, opt): the path to the output figure directory.
                                  Default is None. If None is passed, the figures will be saved
                                  in the current directory.
            savefile (bool, opt): whether to save the data or not.
                                  Default is False to not produce data files in the notebooks.
                                  Consider that it may be suggested to have it True by default
                                  when running the diagnostic from the command line.
            outputdir (str, opt): the path to the output directory.
                                  Default is None. If None is passed, the data will be saved
                                  in the current directory.
            filename (str, opt):  the custon name of the output file.
                                  Default is None. 
                                  Please consider changing it to the default value that you want to use.
            loglevel (str):       the log level.
                                  Default is 'WARNING'.
                                  Please do not change it. It is used with the same default value
                                  in the other diagnostics and in the framework.
                                  Possible values are 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL',
                                  with decreasing order of verbosity and increasing importance.

        Returns:
            None

        Raises:
        """

        # Configure logger
        self.loglevel = loglevel # Set the log level to the one passed to the class
        self.logger = log_configure(self.loglevel, 'Dummy') # Please change the name of the logger to the name of your diagnostic

    def run(self):
        """The run method.""
