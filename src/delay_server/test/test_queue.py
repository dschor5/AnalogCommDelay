""" Test for delay.queue module. """
import unittest
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

    def test_push_pop_no_delay(self):
        self.assertEqual(len(self.__queue), 0)
        print("1111")
        ret = self.__queue.pop()
        self.assertIsNone(ret)
        print("2222")
        for i in range(1,5):
            print("***" * (i+1))
            print("pre-push " + str(i))
            ret = self.__queue.push("test" + str(i))
            self.assertEqual(ret, 1)
            print("pre-len " + str(i))
            self.assertEqual(len(self.__queue), 1)
            print("pre-pop " + str(i))
            ret = self.__queue.pop()
            print("pre-len " + str(i) + " ret=" + str(ret))
            #self.assertEqual(ret, "test" + str(i))
            print(self.__queue)
            self.assertEqual(len(self.__queue), 0)
            print("***" * (i+1))

        for i in range(5):
            ret = self.__queue.push("test" + str(i))
            self.assertEqual(ret, i+1)

    def test_push_pop_with_delay(self):
        self.assertEqual(len(self.__queue), 0)

        delay = 0.2 # sec

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
    
    def test_str(self):
        self.assertEqual(len(self.__queue), 0)
        ret = self.__queue.__str__()
        self.assertEqual(ret, "[]")

        for i in range(5):
            ret = self.__queue.push(b'\x00' * (i+1))
            self.assertEqual(ret, i+1)
            exp = "["
            for j in range(1, i+2):
                exp += str(j) + ", "
            exp += "]"
            ret = self.__queue.__str__()
            self.assertEqual(ret, exp)
            
        
