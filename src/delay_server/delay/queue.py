"""Delay queue."""
import time
import logging

# Disable pylint warning for import errors.
# pylint: disable=E0401
from delay.delay import CommDelay
from common.lock import LockTimeout


class DelayQueue:
    """Delay Queue."""

    # Default timeout for waiting for lock.
    __TIMEOUT = 5.0

    def __init__(self):
        """Initialize."""
        # Lock to make the queue thread safe.
        self._lock = LockTimeout()

        # Data structure for the queue.
        self._list = []

        # Delay configuration.
        self._delay = CommDelay()

    def clear(self):
        """Clear queue."""
        with self._lock.acquire_timeout(self.__TIMEOUT):
            # Logger object.
            logger = logging.getLogger(self.__class__.__name__)
            logger.info('Clear %d from queue.', len(self._list))
            self._list.clear()

    def pop(self):
        """Pop message from queue after the delay expired."""
        ret = None
        with self._lock.acquire_timeout(self.__TIMEOUT) as r:
            print("LOCK " + str(r))
            if len(self._list) > 0:
                delta = time.monotonic() - self._list[0][0]
                if delta > self._delay.time:
                    ret = self._list.pop(0)[1]
        return ret

    def push(self, value):
        """Push message into the queue. Adds a timestamp."""
        with self._lock.acquire_timeout(self.__TIMEOUT) as r:
            print("LOCK " + str(r))
            self._list.append((time.monotonic(), value))
            length = len(self._list)
        return length

    def __len__(self):
        """Return length of the queue."""
        with self._lock.acquire_timeout(self.__TIMEOUT):
            return len(self._list)

    def __str__(self):
        """Return length of each element in the queue."""
        with self._lock.acquire_timeout(self.__TIMEOUT):
            ret = "["
            for i in self._list:
                ret += str(len(i[1])) + ", "
            ret += "]"
        return ret
