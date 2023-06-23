"""Dummy diagnostic for testing purposes"""
import os
import sys
import xarray as xr

from aqua.logger import log_configure
from aqua.util import load_yaml
from aqua.reader import Reader

# This is to access the dummy_func.py file
# Please import only functions that are used in the class
# and not the entire module
sys.path.insert(0, '../')
from dummy_func import dummy_func


class DummyDiagnostic():
    """Dummy diagnostic class"""
    def __init__(self, model=None, exp=None, source=None,
                 configdir=None, regrid=None,
                 timemean=False, freq=None,
                 var=None, custom_diagvar="I'm a custom variable",
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
            var (str, opt):       the variable name to be used by the Reader class in the retrieve method.
                                  Default is None.
                                  Please change it to the default value that you want to use,
                                  considering that it will be the one used by the Reader class
                                  if the user does not specify it.
                                  It may be a list as well, since the Reader class can handle lists.
            custom_diagvar (str): the variable name to be used by the Reader class in the compute method.
                                  Default is "I'm a custom variable".
                                  Please change it to the default value that you want to use,
                                  add more of them if your diagnostic needs more than one variable.
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
            ValueError: if model, exp or source are not specified.
            ValueError: if freq is not specified and timemean is True.
            ValueError: if var is not specified.
        """

        # Configure logger
        self.loglevel = loglevel  # Set the log level to the one passed to the class
        self.logger = log_configure(self.loglevel, 'Dummy') # Please change the name of the logger to the name of your diagnostic

        # Reader variables
        # This is a block that initializes the variables that will be used by the Reader class.
        # Please adapt it to your needs.
        # Consider that this example is instantiating only one Reader class.
        # If you need to instantiate more than one Reader class, please adapt it to your needs.
        # You may instantiate more Reader classes here or you instead instantiate them
        # on multiple instances of the diagnostic class.
        # It will depend on your internal methods.
        if model:  # here model, exp, source are mandatory, check if it is the case for your diagnostic.
            self.model = model
        else:
            raise ValueError('model must be specified')

        if exp:
            self.exp = exp
        else:
            raise ValueError('exp must be specified')

        if source:
            self.source = source
        else:
            raise ValueError('source must be specified')

        self.regrid = regrid  # adapt or remove if you do not need it
        if self.regrid is None:
            self.logger.warning('No regridding will be performed')
        self.logger.info('Regridding resolution: {}'.format(self.regrid))

        self.timemean = timemean  # adapt or remove if you do not need it
        self.freq = freq
        if self.timemean:
            self.logger.warning('Time mean will be computed')
            if self.freq is None:
                raise ValueError('freq must be specified if timemean is True')
            self.logger.info('Time mean frequency: {}'.format(self.freq))
        # Consider that the Reader has more arguments that can be passed to it.
        # Please adapt the code to your needs.
        # You can find more information about the Reader class in the documentation.

        # Diagnostic variables
        # This is a block that initializes the variables that will be used by the diagnostic.
        # Please adapt it to your needs.
        self.var = var  # adapt or remove if you do not need it
        if self.var is None:
            raise ValueError('var must be specified')  # you may have (and probably should) a default different from None
        # If you want to retrieve all data consider removing the var argument from the class __init__.

        self.custom_diagvar = custom_diagvar
        self.logger.info('Custom diagnostic variable: {}'.format(self.custom_diagvar))

        self.configdir = configdir  # adapt or remove if you do not need it
        if self.configdir is None:
            self.logger.warning('No config directory specified')
        else:
            self.logger.info('Config directory: {}'.format(self.configdir))

        # Here you can load the config files if you have any.
        try:
            configname = 'config.yaml'  # adapt or remove if you do not need it
            configpath = os.path.join(self.configdir, configname)  # adapt or remove if you do not need it
            self.config = load_yaml(configpath)  # customise the name of the config file if you need it
        except (FileNotFoundError, TypeError):
            self.logger.warning('Config file not found')
            self.logger.warning('Please be sure all the settings are passed as arguments')
            self.config = None

        # Output variables
        # This is a block that initializes the variables that will be used to save the data.
        # Please adapt it to your needs.
        # Here we set two folders, one for the figures and one for the data.
        self.savefig = savefig  # adapt or remove if you do not need it
        if outputfig:
            self.outputfig = outputfig
        else:
            self.logger.info('No figure folder specified, trying to use the config file setting')
            try:
                self.outputfig = self.config['outputfig']
                # Check if the path exists
                if not os.path.exists(self.outputfig):
                    self.logger.warning('Figure output folder does not exist, creating it')
                    os.makedirs(self.outputfig)
            except (KeyError, TypeError):
                self.logger.warning('No figure folder specified, using the current directory')
                self.outputfig = os.getcwd()
        self.logger.debug('Figure output folder: {}'.format(self.outputfig))

        self.savefile = savefile  # adapt or remove if you do not need it
        if outputdir:
            self.outputdir = outputdir
        else:
            self.logger.info('No data folder specified, trying to use the config file setting')
            try:
                self.outputdir = self.config['outputdir']
                # Check if the path exists
                if not os.path.exists(self.outputdir):
                    self.logger.warning('Data output folder does not exist, creating it')
                    os.makedirs(self.outputdir)
            except (KeyError, TypeError):
                self.logger.warning('No data folder specified, using the current directory')
                self.outputdir = os.getcwd()
        self.logger.debug('Data output folder: {}'.format(self.outputdir))

        self.filename = filename  # adapt or remove if you do not need it
        if self.filename is None:
            self.logger.info('No filename specified, using the config file setting')
            try:
                self.filename = self.config['filename']
            except (KeyError, TypeError):
                self.logger.warning('No filename specified, using the default one')
                self.filename = 'dummy.nc'
        self.logger.debug('Output filename: {}'.format(self.filename))

        # Initialize the Reader class
        self._reader()  # self has not to be passed to the method as it is contained in the class

        # Plese if some more initialization is needed for the diagnostic, do it in this functions.

    def _reader(self):
        """The reader method.
        This method initializes the Reader class.

        Args:
            None

        Returns:
            None
        """

        self.reader = Reader(model=self.model, exp=self.exp, source=self.source, regrid=self.regrid,
                             timemean=self.timemean, freq=self.freq, loglevel=self.loglevel)
        self.logger.debug('Reader class initialized')

    def retrieve(self):  # Notice that self should be contained in every method
        """The retrieve method.
        This method retrieves the data from the Reader class.
        It is an explicit method, so no "_" at the beginning.
        If your methods are not explicit, add "_" at the beginning of the method name.

        Args:
            None

        Returns:
            None

        Raises:
            ValueError: if the variable is not found
        """

        try:
            self.data = self.reader.retrieve(var=self.var)
        except ValueError:
            try:
                self.logger.warning('Variable {} not found'.format(self.var))
                self.logger.warning('Trying to retrieve without fixing')
                self.data = self.reader.retrieve(var=self.var, fix=False)
            except ValueError:
                raise ValueError('Variable {} not found'.format(self.var))
        self.logger.info('Data retrieved')

    def fldmean(self):
        """The fldmean method.
        This method computes the field mean of the retrieved data.
        It is an example of method that does not use of external functions of the module

        Args:
            None

        Returns:
            None

        Raises:
            TypeError: if the variable is not a string
        """
        if self.var is str:
            self.fldmean = self.reader.fldmean(self.data)
            self.logger.info('Field mean computed')
            self.logger.info('Field mean: {}'.format(self.fldmean))
        else:
            raise TypeError('Variable is not a string, cannot compute field mean')

    def multiplication(self):
        """The multiplication method.
        This method computes the multiplication of the retrieved data.
        It is an example of method that uses of external functions of the module

        Args:
            None

        Returns:
            None
        """

        self.multiplication = dummy_func(self.data)  # dummy_func is a function defined in the module

    def _secret_method(self):
        """The secret method.
        This method is a secret one, so it has "_" at the beginning.
        If your methods are explicit, remove "_" at the beginning of the method name.
        """
        self.logger.debug('This is a secret method')

# Notice that more methods can be added to the class, and they can be explicit or not.
# Consider adding or not plot methods, depending on your needs.

