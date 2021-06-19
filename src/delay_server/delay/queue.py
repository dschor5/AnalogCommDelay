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
    __TIMEOUT = 0.5

    def __init__(self):
        """Initialize."""
        # Lock to make the queue thread safe.
        self._lock = LockTimeout()

        # Data structure for the queue.
        self._list = []

        # Delay configuration.
        self._delay = CommDelay()

        self._logger = logging.getLogger(self.__class__.__name__)

    def clear(self):
        """Clear queue."""
        with self._lock.acquire_timeout(self.__TIMEOUT) as lock:
            if lock:
                self._logger.info('Clear %d from queue.', len(self._list))
                self._list.clear()
            else:
                self._logger.error('Lock failed. Cannot clear queue.')

    def pop(self):
        """Pop message from queue after the delay expired."""
        ret = None
        with self._lock.acquire_timeout(self.__TIMEOUT) as lock:
            if lock:
                if len(self._list) > 0:
                    delta = time.monotonic() - self._list[0][0]
                    if delta >= self._delay.time:
                        ret = self._list.pop(0)[1]
            else:
                self._logger.error('Lock failed. Cannot pop queue.')
        return ret

    def push(self, value):
        """Push message into the queue. Adds a timestamp."""
        length = None
        with self._lock.acquire_timeout(self.__TIMEOUT) as lock:
            if lock:
                self._list.append((time.monotonic(), value))
                length = len(self._list)
            else:
                self._logger.error('Lock failed. Cannot push queue.')
        return length

    def __len__(self):
        """Return length of the queue."""
        length = 0
        with self._lock.acquire_timeout(self.__TIMEOUT) as lock:
            if lock:
                length = len(self._list)
            else:
                self._logger.error('Lock failed. Cannot calc queue length.')
        return length

    def __str__(self):
        """Return length of each element in the queue."""
        ret = ""
        with self._lock.acquire_timeout(self.__TIMEOUT) as lock:
            if lock:
                ret = "["
                for i in self._list:
                    ret += str(len(i[1])) + ", "
                ret += "]"
            else:
                ret = "ERROR: Cannot get lock for queue.__str__"
        return ret
