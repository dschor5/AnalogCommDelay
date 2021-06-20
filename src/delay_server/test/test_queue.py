""" Test for delay.queue module. """
import time

# pylint: disable=E0401
from test.test_class import TestClass
from delay.delay import CommDelay
from delay.queue import DelayQueue


class TestQueue(TestClass):
    """Test class for main file."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__queue = None

    def setUp(self):
        """ Always create a new queue before running a test."""
        self.__queue = DelayQueue()
        self.__queue.clear()
        config = CommDelay()
        config.set_override(None)

    def test_init(self):

        # Create object
        self.assertIsNotNone(self.__queue)

        # Create another queue to show they are unique instances.
        other_queue = DelayQueue()
        self.assertIsNotNone(other_queue)
        self.assertNotEqual(self.__queue, other_queue)

    def test_clear(self):
        # Clear empty queue
        self.assertTrue(self.__queue.clear())
        self.assertEqual(len(self.__queue), 0)

        # Clear queue with data
        self.assertEqual(len(self.__queue), 0)
        for i in range(1, 5):
            val = b'\x01' * (i + 1)
            ret = self.__queue.push(val)
            self.assertEqual(ret, i)
        self.assertTrue(self.__queue.clear())
        self.assertEqual(len(self.__queue), 0)

        # Failed to acquire lock
        self.assertTrue(self.__queue._lock.acquire())
        self.assertFalse(self.__queue.clear())
        self.assertTrue(self.__queue._lock.release())

    def test_push_pop_no_delay(self):
        num_test = 5

        # CPop empty queue
        self.assertEqual(len(self.__queue), 0)
        self.assertIsNone(self.__queue.pop())

        # Add/remove elements from the queue.
        for i in range(1, num_test):
            ret = self.__queue.push(b'\x01' * (i+1))
            self.assertEqual(ret, 1)
            self.assertEqual(len(self.__queue), 1)
            ret = self.__queue.pop()
            self.assertEqual(ret, b'\x01' * (i+1))
            self.assertEqual(len(self.__queue), 0)

        # Test queue order maintained.
        # 1) Add a few elements
        for i in range(1, num_test):
            ret = self.__queue.push(b'\x01' * (i+1))
            self.assertEqual(ret, i)
            self.assertEqual(len(self.__queue), i)
        # 2) Pop them in order.
        for i in range(1, num_test):
            self.assertEqual(len(self.__queue), num_test-i)
            ret = self.__queue.pop()
            self.assertEqual(ret, b'\x01' * (i+1))
            self.assertEqual(len(self.__queue), num_test-i-1)
        # 3) Pop empty queue
        self.assertEqual(len(self.__queue), 0)
        self.assertIsNone(self.__queue.pop())

        # Push None object
        self.assertEqual(len(self.__queue), 0)
        self.assertEqual(self.__queue.push(None), 0)
        self.assertEqual(len(self.__queue), 0)

        # Failed to acquire lock for push
        self.assertTrue(self.__queue._lock.acquire())
        self.assertFalse(self.__queue.push(b'\x05'))
        self.assertTrue(self.__queue._lock.release())

        # Failed to acquire lock for pop
        self.assertEqual(self.__queue.push(b'\x05'), 1)
        self.assertTrue(self.__queue._lock.acquire())
        self.assertIsNone(self.__queue.pop())
        self.assertTrue(self.__queue._lock.release())

    def test_push_pop_with_delay(self):
        self.assertEqual(len(self.__queue), 0)

        delay = 0.1  # sec

        c = CommDelay()
        c.set_override(delay)
        self.assertEqual(c.time, delay)

        ret = self.__queue.push("test")
        self.assertEqual(ret, 1)
        ret = self.__queue.pop()
        self.assertIsNone(ret)
        time.sleep(delay)
        ret = self.__queue.pop()
        self.assertEqual(ret, "test")

    def test_len(self):
        self.assertEqual(len(self.__queue), 0)
        self.assertEqual(self.__queue.push(b'\x05'), 1)
        self.assertTrue(self.__queue._lock.acquire())
        self.assertEqual(len(self.__queue), 0)
        self.assertTrue(self.__queue._lock.release())

    def test_str(self):
        num_test = 5

        # Print empty queue
        self.assertEqual(len(self.__queue), 0)
        ret = self.__queue.__str__()
        self.assertEqual(ret, "[]")

        # Print incremental size queue
        for i in range(num_test):
            ret = self.__queue.push(b'\x00' * (i+1))
            self.assertEqual(ret, i+1)
            exp = "["
            for j in range(1, i+2):
                exp += str(j) + ", "
            exp += "]"
            ret = self.__queue.__str__()
            self.assertEqual(ret, exp)

        # Print empty queue (check for residual content)
        self.assertTrue(self.__queue.clear())
        ret = self.__queue.__str__()
        self.assertEqual(ret, "[]")
        
        self.assertTrue(self.__queue._lock.acquire())
        ret = self.__queue.__str__()
        self.assertTrue(ret.startswith('ERROR'))
        self.assertTrue(self.__queue._lock.release())
