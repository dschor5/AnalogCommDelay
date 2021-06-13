""" Singleton class to setup logger for unit test. """

import logging
import logging.config
import yaml
import os

class TestLog:

    # Singleton instance
    __instance = None

    __LOG_CONFIG = 'test/log.yaml'
    __LOG_FILE   = 'test/delay_server_test.log'

    def __new__(cls):
        """ Singleton constructor for DelayConfig object. """
        if not TestLog.__instance:
            TestLog.__instance = super(TestLog, cls).__new__(cls)
        return TestLog.__instance

    def __init__(self):
        if not hasattr(self, '_delay_logger'):

            if not os.path.exists(TestLog.__LOG_CONFIG):
                raise RuntimeError('Cannot load unit test log config.')

            needs_rollover = os.path.isfile(TestLog.__LOG_FILE)

            with open(TestLog.__LOG_CONFIG, 'rt') as fp:
                config = yaml.safe_load(fp.read())
                logging.config.dictConfig(config)

            self._delay_logger = logging.getLogger()

            if needs_rollover:
                self._delay_logger.handlers[0].doRollover()
