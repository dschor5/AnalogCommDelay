import unittest
from src.util.crc16 import CRC16

class TestDelayPacket(unittest.TestCase):
    """Test class for main file."""

    def test_calc_crc(self):
        """ Test CRC16 based on https://crccalc.com """
        self.assertEqual(CRC16.calc_crc(None), 0xFFFF)
