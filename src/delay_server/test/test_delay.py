""" Test for delay.config module. """
import unittest

# pylint: disable=E0401
from test.test_class import TestClass
from delay.delay import CommDelay

class TestCommDelay(TestClass):
    """Test class for main file."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        """ Setup before each run. Resets DelayConfig object to defaults. """
        config = CommDelay()
        config.clear_override()
        config.load_file(None)

    def test_init(self):

        # Create object
        config1 = CommDelay()
        self.assertIsNotNone(config1)

        # Verify Singleton
        config2 = CommDelay()
        self.assertIsNotNone(config2)
        self.assertEqual(config1, config2)

        # Default values
        self.assertEqual(config1.time, 0)
        self.assertIsNone(config1.filename)

    def test_load_file(self):
        config = CommDelay()

        # Default value for filename
        self.assertIsNone(config.filename, None)

        config.load_file("test_config.txt")
        self.assertEqual(config.filename, "test_config.txt")

    def test_override(self):
        config = CommDelay()
        config.set_override(5)
        self.assertEqual(config.time, 5)
        config.clear_override()
        self.assertEqual(config.time, 0)
