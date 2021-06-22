""" Test for delay.queue module. """
# Disable pylint warning for import errors.
# pylint: disable=E0401
from test.test_custom_class import TestClass
from delay_server.delay.consumer import ConsumerThread
from delay_server.delay.queue import DelayQueue


class TestConsumer(TestClass):
    """Test class for main file."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__port = 1000
        self.__queue = DelayQueue()
        self.__server = None

    def setUp(self):
        self.__server = ConsumerThread(self.__port, self.__queue)

    def tearDown(self):
        if self.__server is not None:
            self.__server.stop_thread()
            self.__server = None

    def test_run(self):
        # Needed for code coverage only.
        self.__server.run(**dict())
        self.__server.stop_thread()
