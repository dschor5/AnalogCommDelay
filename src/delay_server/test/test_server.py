""" Test for delay.queue module. """
import unittest

# pylint: disable=E0401
from delay.server import SocketServer
from delay.producer import ProducerThread
from delay.queue import DelayQueue

class TestServer(unittest.TestCase):
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

    def test_init(self):

        # Test abstract constructor
        with self.assertRaises(TypeError):
            SocketServer("Test", self.__port, self.__queue)

        # Test constructor
        self.assertIsNotNone(self.__server)

        # Test property name
        self.assertEqual(self.__server.server_name, "Producer")


    def test_create_socket(self):
        self.assertIsNone(SocketServer.create_socket(None))
        ret = SocketServer.create_socket(1000)
        self.assertIsNotNone(ret)
        ret.close()

    def test_thread(self):
        self.assertTrue(self.__server.start_thread())
        self.assertFalse(self.__server.start_thread())

    def test_run(self):
        # Needed for code coverage only. 
        SocketServer.run(dict())
        
