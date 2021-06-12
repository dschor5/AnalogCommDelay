""" Test for delay.queue module. """
import unittest
import time

# pylint: disable=E0401
from delay.config import DelayConfig
from delay.queue import DelayQueue

class TestQueue(unittest.TestCase):
    """Test class for main file."""

    def __init__(self, *args, **kwargs):
        super(TestQueue, self).__init__(*args, **kwargs)
        self.__queue = None

    def setUp(self):
        """ Always create a new queue before running a test."""
        self.__queue = DelayQueue()

    def test_init(self):
        """ Test CRC16 based on https://crccalc.com """

        # Create object
        self.assertIsNotNone(self.__queue)

        # Create another queue to show they are unique instances.
        other_queue = DelayQueue()
        self.assertIsNotNone(other_queue)
        self.assertNotEqual(self.__queue, other_queue)

    def test_push_pop_no_delay(self):
        self.assertEqual(len(self.__queue), 0)

        for i in range(5):
            ret = self.__queue.push("test" + str(i))
            self.assertEqual(ret, 1)
            ret = self.__queue.pop()
            self.assertEqual(ret, "test" + str(i))
            self.assertEqual(len(self.__queue), 0)

        for i in range(5):
            ret = self.__queue.push("test" + str(i))
            self.assertEqual(ret, i+1)

