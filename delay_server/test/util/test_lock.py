""" Test for delay.queue module. """
# pylint: disable=E0401
from test.test_custom_class import TestClass
from delay_server.util.lock import LockTimeout


class TestLock(TestClass):
    """Test class for main file."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__lock = None
        self.__TIMEOUT = 0.1

    def setUp(self):
        self.__lock = LockTimeout()

    def test_lock(self):
        # Acquire/release
        self.assertTrue(self.__lock.acquire())
        self.assertTrue(self.__lock.locked())
        self.assertTrue(self.__lock.release())
        self.assertFalse(self.__lock.release())

        # Acquire_timeout/release - FAIL
        self.assertTrue(self.__lock.acquire())
        self.assertTrue(self.__lock.locked())
        with self.__lock.acquire_timeout(self.__TIMEOUT) as lock:
            self.assertFalse(lock)
        self.assertTrue(self.__lock.release())
        self.assertFalse(self.__lock.locked())

        # Acquire_timeout/release - SUCCESS
        self.assertFalse(self.__lock.locked())
        with self.__lock.acquire_timeout(self.__TIMEOUT) as lock:
            self.assertTrue(lock)
            self.assertTrue(self.__lock.locked())
        self.assertFalse(self.__lock.release())
        self.assertFalse(self.__lock.locked())
