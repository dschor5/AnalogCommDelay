""" Test for delay.config module. """
import unittest
import logging

# pylint: disable=E0401
from test.log_setup import TestLog

class TestClass(unittest.TestCase):
    """Test class for main file."""

    _logger = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        TestLog()
        TestClass._logger = logging.getLogger("TestClass")

    @classmethod
    def setUpClass(cls):
        TestClass._logger.info("START " + cls.__name__)

    @classmethod
    def tearDownClass(cls):
        TestClass._logger.info("END " + cls.__name__)
