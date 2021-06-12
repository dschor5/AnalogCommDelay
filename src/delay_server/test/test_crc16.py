""" Test for common.crc16 module. """
import unittest

 # pylint: disable=E0401
from common.crc16 import CRC16

class TestCrc16(unittest.TestCase):
    """Test class for main file."""

    def test_calc_crc(self):
        """ Test CRC16 based on https://crccalc.com """

        # Input validation
        self.assertEqual(CRC16.calc_crc(None), None)
        self.assertEqual(CRC16.calc_crc(1), None)

        # Calc CRC without initial seed.
        crc = CRC16.calc_crc(bytes(b'\x01'))
        self.assertEqual(crc, 0xF1D1)
        crc = CRC16.calc_crc(bytes(b'\x01\x02'))
        self.assertEqual(crc, 0x0E7C)

        # Calc CRC with initial seed
        crc = CRC16.calc_crc(bytes(b'\x01'))
        crc = CRC16.calc_crc(bytes(b'\x02'), crc)
        self.assertEqual(crc, 0x0E7C)
        crc = CRC16.calc_crc(bytes(b'\x01\x02'))
        crc = CRC16.calc_crc(bytes(b'\x01\x02'), crc)
        self.assertEqual(crc, 0x8F67)
