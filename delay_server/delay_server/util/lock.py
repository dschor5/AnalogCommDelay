"""Implements a Lock with a timeout."""
import threading
import contextlib
import time


class LockTimeout:
    """Lock with Timeout."""

    def __init__(self):
        """Initialize."""
        self.__lock = threading.Lock()

    def acquire(self, blocking: bool = True, timeout: int = -1) -> bool:
        """Acquire function. Matches threading.Lock.acquire interface."""
        return self.__lock.acquire(blocking, timeout)

    def release(self) -> bool:
        """Release lock. Matches threading.Lock.release interface."""
        ret = True
        try:
            self.__lock.release()
        except RuntimeError:
            ret = False
        return ret

    @contextlib.contextmanager
    def acquire_timeout(self, lock_timeout: int) -> bool:
        """Context manager to acquire with timeout."""
        ret = self.__lock.acquire(blocking=True, timeout=lock_timeout)
        yield ret
        if ret:
            self.__lock.release()

    def locked(self) -> bool:
        """Return True if locked."""
        return self.__lock.locked()
