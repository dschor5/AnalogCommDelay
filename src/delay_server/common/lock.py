"""Implements a Lock with a timeout."""
import threading
import contextlib


class LockTimeout:
    """Lock with Timeout."""

    def __init__(self):
        """Initialize."""
        self.__lock = threading.Lock()

    def acquire(self, blocking=True, timeout=-1):
        """Acquire function. Matches threading.Lock.acquire interface."""
        return self.__lock.aquire(blocking, timeout)

    def release(self):
        """Release lock. Matches threading.Lock.release interface."""
        return self.__lock.release()

    @contextlib.contextmanager
    def acquire_timeout(self, lock_timeout):
        """Aquire function with timeout."""
        ret = self.__lock.acquire(blocking=True, timeout=lock_timeout)
        try:
            yield ret
        finally:
            self.__lock.release()
