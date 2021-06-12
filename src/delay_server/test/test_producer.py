""" Test for delay.queue module. """
import unittest
import time

# pylint: disable=E0401
from delay.producer import ProducerThread
from delay.queue import DelayQueue


class TestProducer(unittest.TestCase):
    """Test class for main file."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__port = 1000
        self.__queue = DelayQueue()
        self.__server = None
        
    def setUp(self):
        self.__server = ProducerThread(self.__port, self.__queue)

    def tearDown(self):
        if self.__server is not None:
            self.__server.stop_thread()
            self.__server = None

    def test_run(self):
        # Needed for code coverage only. 
        ProducerThread.run(dict())

        ProducerThread.run(dict(sock=None))

            
        
