"""Singleton class to setup logger for unit test."""

import logging
import logging.config
import yaml
import os


class TestLog:
    """Initialize log file for unit test."""

    # Singleton instance
    __instance = None

    __LOG_CONFIG = 'test/log.yaml'
    __LOG_FOLDER = 'test/log'
    __LOG_FILE = 'delay_server_test.log'

    def __new__(cls):
        """Singleton constructor for DelayConfig object."""
        if not TestLog.__instance:
            TestLog.__instance = super(TestLog, cls).__new__(cls)
        return TestLog.__instance

    def __init__(self):
        if not hasattr(self, '_delay_logger'):

            if not os.path.exists(TestLog.__LOG_CONFIG):
                raise RuntimeError('Cannot load unit test log config.')

            if not os.path.exists(TestLog.__LOG_FOLDER):
                os.makedirs(TestLog.__LOG_FOLDER)

            needs_rollover = os.path.isfile(TestLog.__LOG_FOLDER +
                                            "/" + TestLog.__LOG_FILE)

            with open(TestLog.__LOG_CONFIG, 'rt') as fp:
                config = yaml.safe_load(fp.read())
                logging.config.dictConfig(config)

            self._delay_logger = logging.getLogger()

            if needs_rollover:
                self._delay_logger.handlers[0].doRollover()
