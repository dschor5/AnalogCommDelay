"""Test for common.crc16 module."""
# pylint: disable=E0401
from test.test_custom_class import TestClass
from delay_server.util.crc16 import CRC16


class TestCrc16(TestClass):
    """Test class for main file."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_calc_crc(self):
        # Based on https://crccalc.com

        # Input validation
        with self.assertRaises(AttributeError):
            CRC16.calc_crc(None)
        with self.assertRaises(TypeError):
            CRC16.calc_crc("string_input")

        # Calc CRC without initial seed.
        crc = CRC16.calc_crc(b'\x01')
        self.assertEqual(crc, 0xF1D1)
        crc = CRC16.calc_crc(b'\x01\x02')
        self.assertEqual(crc, 0x0E7C)

        # Calc CRC with initial seed
        crc = CRC16.calc_crc(b'\x01')
        crc = CRC16.calc_crc(b'\x02', crc)
        self.assertEqual(crc, 0x0E7C)
        crc = CRC16.calc_crc(b'\x01\x02')
        crc = CRC16.calc_crc(b'\x01\x02', crc)
        self.assertEqual(crc, 0x8F67)
