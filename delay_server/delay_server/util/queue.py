import time
import logging

from delay_server.delay.delay import CommDelay
from delay_server.util.lock import LockTimeout
from delay_server.util.exceptions import LockError


class DelayQueue:
    """Thread-safe queue (first-in-first-out) with time delay pop operations.

    Objects are pushed into the queue by calling :meth:`push()`. The method
    also adds a timestamp, :math:`t_{obj}`, given by :py:func:`time.monotonic`.

    Objects are poppoed off the queue in by calling :py:meth:`pop()`.
    The method compares the object timestamp agains thte current time,
    :math:`t_{current}` and the current delay, :math:`t_{delay}` as given by
    :class:`delay_server.delay.delay.CommDelay`. In order for an object to be
    removed from the queue it must satisfy:
    :math:`t_{current} - t_{obj} > t_{delay}`
    """

    # Default timeout (in sec) for waiting for lock.
    _TIMEOUT = 0.25

    def __init__(self, logger: logging.Logger = None, timeout: int = None):
        """Initialize a DelayQueue object.

        Args:
            logger (logging.Logger): Logger object linked to parent class. If
                not provided, then get a logger based on the class name.
            timeout (int): Optional; Timeout in seconds for accessing lock for
                queue operations. If not provided, defaults to 0.1sec.

        Returns:
            bool: A DelayQueue object.
        """
        # Lock to make the queue thread safe.
        self._lock = LockTimeout()

        # Data structure to store first-in-first-out queue.
        self._list = []

        # Delay configuration.
        self._delay = CommDelay()

        # Assign a logger
        self._logger = logger
        if self._logger is None:
            self._logger = logging.getLogger(self.__class__.__name__)

        # Assign timeout
        if timeout is not None:
            self._TIMEOUT = timeout

    def clear(self) -> int:
        """Clear the queue. Logs number of messages deleted.

        Returns:
            int: Number of messages cleared from the queue.

        Raises:
            LockError: Failed to obtain lock for queue.
        """
        if not self._lock.acquire(blocking=True, timeout=self._TIMEOUT):
            raise LockError("Failed to get lock to clear queue.")
        length = len(self._list)
        self._logger.info('Clear %d from queue.', length)
        self._list.clear()
        self._lock.release()
        return length

    def pop(self) -> object:
        """Pop message provided timeout is satisfied. See class description.

        Returns:
            object:
                - :class:`None` if list is empty
                - :class:`None` if not empty and top does not satisfy timeout.
                - :class:`object` from the queue if timeout is satisfied.

        Raises:
            LockError: Failed to obtain lock for queue.
        """
        if not self._lock.acquire(blocking=True, timeout=self._TIMEOUT):
            raise LockError("Failed to get lock to pop queue.")

        ret = None
        if len(self._list) > 0:
            delta = time.monotonic() - self._list[0]['timestamp']
            if delta >= self._delay.time:
                ret = self._list.pop(0)['data']
        self._lock.release()
        return ret

    def push(self, obj: object) -> int:
        """Push :class:`object` into the queue.

        Args:
            obj (object): Data to push into the queue. Cannot be None.

        Returns:
            int: Queue size

        Raises:
            TypeError: Param obj is none.
            LockError: Failed to obtain lock for queue.
        """
        if obj is None:
            raise AttributeError('Push value cannot be None.')

        if not self._lock.acquire(blocking=True, timeout=self._TIMEOUT):
            raise LockError("Failed to get lock to push into the queue.")

        self._list.append(dict(timestamp=time.monotonic(), data=obj))
        length = len(self._list)
        self._lock.release()

        return length

    def __len__(self) -> int:
        """Return queue size.

        Returns:
            int: Queue size

        Raises:
            LockError: Failed to obtain lock for queue.
        """
        if not self._lock.acquire(blocking=True, timeout=self._TIMEOUT):
            raise LockError("Failed to get lock to calc length of queue.")

        length = len(self._list)
        self._lock.release()
        return length

    def __str__(self) -> str:
        """Return string representation of queue contents.

        Returns:
            str: Concatenate the string representation of all objects in the
                queue. If the item is a :class:`bytes` or :class:`bytearray`
                then only the length is shown.

        Raises:
            LockError: Failed to obtain lock for queue.
        """
        if not self._lock.acquire(blocking=True, timeout=self._TIMEOUT):
            raise LockError("Failed to get lock to see queue contents.")

        ret = "["
        for i in self._list:
            if isinstance(i['data'], (bytes, bytearray)):
                ret += str(len(i['data'])) + ", "
            else:
                ret += str(i['data']) + ", "
        ret += "]"
        self._lock.release()
        return ret
