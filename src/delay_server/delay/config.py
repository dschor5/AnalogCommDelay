"""Load Delay Server configuration."""
import configparser
import os
import logging


# Disable pylint error for too many ancestors
# pylint: disable=R0901
class DelayConfig(configparser.ConfigParser):
    """DelayConfig class. Extends ConfigParser."""

    # Singleton instance
    __instance = None

    # Configuration file
    __filename = 'config.ini'

    # Initialized flag
    __initialized = False

    def __new__(cls):
        """Singleton constructor for DelayConfig object."""
        if not DelayConfig.__instance:
            DelayConfig.__instance = super(DelayConfig, cls).__new__(cls)
        return DelayConfig.__instance

    def __init__(self):
        """Initialize variables for this class."""
        if not DelayConfig.__initialized:
            super().__init__(self)
            DelayConfig.__initialized = True
            self._read_config()

    def _read_config(self, filename=None):
        """Read config file."""
        # Access to logger
        logger = logging.getLogger(self.__class__.__name__)

        # Accept filename override for testing purposes
        if filename is None:
            filename = DelayConfig.__filename

        if os.path.exists(filename):
            super().__init__()
            try:
                self.read(filename)
            except configparser.Error:
                logger.critical('Failed to parse log file %s', filename)
                return False
            if not self._validate():
                logger.critical('Failed to validate %s', filename)
                return False
        else:
            logger.critical('Failed to load %s', self.__filename)
            return False
        return True

    def get(self, section, option, **kwargs):
        """Get attributes."""
        ret = None
        try:
            ret = super().get(section, option, **kwargs)
        except configparser.Error:
            logger = logging.getLogger(self.__class__.__name__)
            logger.error('Did not find config[%s][%s]', section, option)
        return ret

    def _validate(self):
        """Validate config file. Check for required params."""
        # TODO: Validate config file
        # Check for required fields to run the program.
        return self.__initialized is not None

    def __repr__(self):
        """Return list of all config fields."""
        rtn = ""
        for cat_name, cat_data in self.items():
            for field_name in cat_data:
                rtn += cat_name + "." + field_name + \
                    " = " + str(self.get(cat_name, field_name)) + "\n"
        return rtn
