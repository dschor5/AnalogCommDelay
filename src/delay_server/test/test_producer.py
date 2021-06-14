""" Test for delay.queue module. """
import unittest
import time
import mock

# pylint: disable=E0401
from test.test_class import TestClass
from delay.producer import ProducerThread
from delay.queue import DelayQueue


class TestProducer(TestClass):
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
        self.__server.run(**dict())
        self.__server.run(**dict(sock=None))
        self.__server.run(**dict(sock=None, stop=None))
        self.__server.run(**dict(sock=None, stop=None, queue=1))
        self.__server.stop_thread()

    def test_receive(self):

        # No message header received
        mock_obj = mock.Mock()
        mock_obj.recv.return_value = 0
        self.assertIsNone(self.__server._receive(mock_obj))

        # Message header with invalid length. 
        mock_obj.recv.return_value = b'\xFFFF'
        self.assertIsNone(self.__server._receive(mock_obj))

            
        
