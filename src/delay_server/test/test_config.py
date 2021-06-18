""" Test for delay.config module. """
import unittest
import mock
import configparser

# pylint: disable=E0401
from test.test_class import TestClass
from delay.config import DelayConfig

class TestDelayConfig(TestClass):
    """Test class for main file."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config = None

    def setUp(self):
        """ Setup before each run. Resets DelayConfig object to defaults. """
        self._config = DelayConfig()

    def test_init(self):
        # Create object
        self.assertIsNotNone(self._config)

        # Verify Singleton
        other = DelayConfig()
        self.assertEqual(self._config, other)

    def test_read_config(self):
        # Read non-existing file
        self.assertFalse(self._config._read_config("dummy.ini"))

        mock_obj = mock.Mock()
        mock_obj.return_value = False
        with mock.patch('delay.config.DelayConfig._validate', mock_obj):
            self.assertFalse(self._config._read_config())

        mock_obj = mock.Mock()
        mock_obj.side_effect = configparser.Error()
        with mock.patch('configparser.ConfigParser.read', mock_obj):
            self.assertFalse(self._config._read_config())

        # Read default config
        self.assertTrue(self._config._read_config())

    def test_getattr(self):
        self.assertTrue(self._config._read_config())
        self.assertIsNone(self._config.get('dummy', 'value'))
        self._config.add_section('dummy')
        self._config.set('dummy', 'value', "1")
        self.assertEqual(self._config.get('dummy', 'value'), "1")
        self._config.remove_option('dummy', 'value')
        self._config.remove_section('dummy')

    def test_repr(self):
        rtr = self._config.__repr__()
        self.assertIsNotNone(rtr)
