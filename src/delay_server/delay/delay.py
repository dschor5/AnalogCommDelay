""" Configurable communication delay.  """

import logging
import threading

class CommDelay:
    """
    Delay Configuration
    """

    # Singleton instance
    __instance = None

    # Flag to mark initialization
    __initialized = False

    def __new__(cls):
        """ Singleton constructor for Delay object. """
        if not CommDelay.__instance:
            CommDelay.__instance = super(CommDelay, cls).__new__(cls)
        return CommDelay.__instance

    def __init__(self):
        """ Initialize variables for this class."""
        if not CommDelay.__initialized:
            CommDelay.__initialized = True
            # Lock for accessing/modifying delay.
            self._lock = threading.Lock()
            # Override delay. If None, then no override.
            self._override = None
            # File containing delay configuration
            self._filename = None
            # Create logger for this module
            self._logger = logging.getLogger(self.__class__.__name__)
            self._logger.info('Create logger "%s"', self.__class__.__name__)

    def load_file(self, p_filename):
        """ Load configuration file. """
        self._logger.info('Load file "%s"', p_filename)
        self._filename = p_filename

    def clear_override(self):
        """ Clear delay override. """
        with self._lock:
            self._override = None
            self._logger.info('Override=None')

    def set_override(self, p_override):
        """ Set override delay. """
        with self._lock:
            self._override = p_override
            self._logger.info('Override=%s', str(self._override))

    @property
    def filename(self):
        """ Filename accessor. """
        return self._filename

    @property
    def time(self):
        """ Time property containing the current delay. """
        curr_delay = 0
        with self._lock:
            if self._override is not None:
                curr_delay = self._override
            else:
                curr_delay = 0
                # TODO read from file
        return curr_delay
