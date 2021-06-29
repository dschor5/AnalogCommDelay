"""Load Delay Server configuration."""
import configparser
import os
import logging


# Disable pylint error for too many ancestors
# pylint: disable=R0901
class DelayConfig(configparser.ConfigParser):
    """DelayConfig class. Extends ConfigParser."""

    # Singleton instance
    _instance = None

    # Configuration file
    _filename = 'config.ini'

    # Initialized flag
    _initialized = False

    def __new__(cls):
        """Singleton constructor for DelayConfig object."""
        if not DelayConfig._instance:
            DelayConfig._instance = super(DelayConfig, cls).__new__(cls)
        return DelayConfig._instance

    def __init__(self, logger: logging.Logger = None):
        """Initialize by reading default config file."""
        if not DelayConfig._initialized:
            super().__init__(self)
            DelayConfig._initialized = True
            self._read_config()
            self._logger = logger
            if self._logger is None:
                self._logger = logging.getLogger(self.__class__.__name__)

    def _read_config(self, filename: str = None) -> bool:
        """Read config file. Returns true on success.

        Args:
            filename (str): Name of config file.

        Returns:
            bool: True on success.
        """
        # Accept filename override for testing purposes
        if filename is None:
            filename = os.path.abspath('.') + "/" + DelayConfig._filename

        # Validate path and ensure it is able to read the file.
        if os.path.exists(filename):
            try:
                self.read(filename)
            except configparser.Error:
                self._logger.critical('Failed to parse log file %s', filename)
                return False
            if not self._validate():
                self._logger.critical('Failed to validate %s', filename)
                return False
        else:
            self._logger.critical('Failed to load %s', filename)
            return False
        return True

    def get(self, section: str, option: str, **kwargs) -> str:
        """Get attribute from config file.

        If the value is not found, return :class:`None` and log an error.

        Args:
            section (str): Config file section name.
            option (str): Config file option name.

        Returns:
            str: Config value or :class:`None` if not found.
        """
        ret = None
        try:
            ret = super().get(section, option, **kwargs)
        except configparser.Error:
            self._logger.error('Did not find config[%s][%s]', section, option)
        return ret

    def getint(self, section, option, **kwargs) -> int:
        """Wrapper for :meth:`get()` that returns integers.

        Args:
            section (str): Config file section name.
            option (str): Config file option name.

        Returns:
            str: Config value. :class:`None` if not found or not an int.
        """
        ret = None
        try:
            ret = super().getint(section, option, **kwargs)
        except ValueError:
            self._logger.error('config[%s][%s] = "%s" - Expected int.',
                               section, option,
                               super().get(section, option, **kwargs))
        return ret

    def getfloat(self, section, option, **kwargs) -> float:
        """Wrapper for :meth:`get()` that returns float.

        Args:
            section (str): Config file section name.
            option (str): Config file option name.

        Returns:
            str: Config value. :class:`None` if not found or not a float.
        """
        ret = None
        try:
            ret = super().getfloat(section, option, **kwargs)
        except ValueError:
            self._logger.error('config[%s][%s] = "%s" - Expected float.',
                               section, option,
                               super().get(section, option, **kwargs))
        return ret

    def getboolean(self, section, option, **kwargs) -> bool:
        """Wrapper for :meth:`get()` that returns boolean.

        Args:
            section (str): Config file section name.
            option (str): Config file option name.

        Returns:
            str: Config value. :class:`None` if not found or not a boolean.
        """
        ret = None
        try:
            ret = super().getboolean(section, option, **kwargs)
        except ValueError:
            self._logger.error('config[%s][%s] = "%s" - Expected boolean.',
                               section, option,
                               super().get(section, option, **kwargs))
        return ret

    def _validate(self) -> bool:
        """Validate config file. Check for required params.

        Returns:
            bool: True if config file is valid.
        """
        # TODO: Validate config file?
        return self._initialized is not None

    def __repr__(self) -> str:
        """Return list of all config fields."""
        rtn = ""
        for cat_name, cat_data in self.items():
            for field_name in cat_data:
                rtn += cat_name + "." + field_name + \
                    " = " + str(self.get(cat_name, field_name)) + "\n"
        return rtn
