""" Delay queue."""

import threading
import time
import logging

from delay_config import DelayConfig

class DelayQueue:
    """ Delay Queue """

    def __init__(self):
        """ Initialize"""
        # Lock to make the queue thread safe.
        self._lock = threading.Lock()

        # Data structure for the queue.
        self._list = []

        # Delay configuration.
        self._delay = DelayConfig()

        # Logger object.
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.info('Create logger "%s"', self.__class__.__name__)

    def pop(self):
        """ Pop message from queue after the delay expired. """
        with self._lock:
            if len(self._list) != 0:
                delta = time.monotonic() - self._list[0][0]
                if delta > self._delay.time:
                    return self._list.pop(0)[1]
        return None

    def push(self, value):
        """ Push message into the queue. Adds a timestamp. """
        with self._lock:
            self._list.append((time.monotonic(), value))

    def __len__(self):
        """ Return length of the queue. """
        with self._lock:
            return len(self._list)

    def __str__(self):
        """ String representation. """
        with self._lock:
            ret = "["
            for i in self._list:
                ret += str(len(i[1])) + ", "
            ret += "]"
        return ret
