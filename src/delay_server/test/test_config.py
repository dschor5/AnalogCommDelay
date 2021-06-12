""" Test for delay.config module. """
import unittest

# pylint: disable=E0401
from delay.config import DelayConfig

class TestDelayConfig(unittest.TestCase):
    """Test class for main file."""

    def setUp(self):
        """ Setup before each run. Resets DelayConfig object to defaults. """
        config = DelayConfig()
        config.clear_override()
        config.load_file(None)

    def test_init(self):
        """ Test init """

        # Create object
        config1 = DelayConfig()
        self.assertIsNotNone(config1)

        # Verify Singleton
        config2 = DelayConfig()
        self.assertIsNotNone(config2)
        self.assertEqual(config1, config2)

        # Default values
        self.assertEqual(config1.time, 0)
        self.assertIsNone(config1.filename)

    def test_load_file(self):
        """ Test loading and parsing a config file. """
        config = DelayConfig()

        # Default value for filename
        self.assertIsNone(config.filename, None)

        config.load_file("test_config.txt")
        self.assertEqual(config.filename, "test_config.txt")

    def test_override(self):
        """ Test override set/clear. """
        config = DelayConfig()
        config.set_override(5)
        self.assertEqual(config.time, 5)
        config.clear_override()
        self.assertEqual(config.time, 0)
