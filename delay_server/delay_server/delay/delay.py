import logging

from delay_server.util.lock import LockTimeout


class CommDelay:
    """Configurable delay.

    The class allows the user to configure the desired delay via a config
    file or override options.
    """

    # Singleton instance
    _instance = None

    # Flag to mark initialization
    _initialized = False

    # Timeout to obtain lock
    _TIMEOUT = 0.5  # sec

    def __new__(cls):
        """Singleton constructor for Delay object."""
        if not CommDelay._instance:
            CommDelay._instance = super(CommDelay, cls).__new__(cls)
        return CommDelay._instance

    def __init__(self, logger: logging.Logger = None):
        """Initialize variables for this class."""
        if not CommDelay._initialized:
            CommDelay._initialized = True
            # Lock for accessing/modifying delay.
            self._lock = LockTimeout()
            # Override delay. If None, then no override.
            self._override = None
            # File containing delay configuration
            self._filename = None
            # Cache curr delay
            self._time_cache = 0
            # Create logger for this module
            self._logger = logger
            if self._logger is None:
                self._logger = logging.getLogger(self.__class__.__name__)
            self._logger.debug('Create logger "%s"', self.__class__.__name__)

    def load_file(self, p_filename: str) -> bool:
        """Load configuration file. Returns true on success."""
        self._logger.info('Load file "%s"', p_filename)
        self._filename = p_filename
        return True

    def clear_override(self) -> bool:
        """Clear delay override. Returns true on success."""
        ret = False
        with self._lock.acquire_timeout(self._TIMEOUT) as lock:
            if lock:
                self._override = None
                self._logger.info('Override=None')
                ret = True
            else:
                self._logger.info('Failed to clear override.')
        return ret

    def set_override(self, p_override: float) -> bool:
        """Set override delay. Returns true on success."""
        if p_override is not None and not isinstance(p_override, (int, float)):
            return False

        ret = False
        with self._lock.acquire_timeout(self._TIMEOUT) as lock:
            if lock:
                self._override = p_override
                self._logger.info('Override=%s', str(self._override))
                ret = True
            else:
                self._logger.info('Failed to override.')
        return ret

    @property
    def filename(self) -> str:
        """Filename accessor."""
        return self._filename

    @property
    def time(self) -> float:
        """Time property containing the current delay."""
        # TODO: If it fails to get the lock, then return self._time_cache
        curr_delay = 0
        with self._lock.acquire_timeout(self._TIMEOUT) as lock:
            if lock:
                if self._override is not None:
                    curr_delay = self._override
                else:
                    curr_delay = 0
                # TODO read from file
                self._time_cache = curr_delay
            else:
                curr_delay = self._time_cache
                self._logger.warning('Using cached delay.')
        return curr_delay
