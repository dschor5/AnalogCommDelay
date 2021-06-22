"""Implementation of CRC-16 CCITT-FALSE Algorithm."""


class CRC16:
    """CRC16 Class."""

    __CRC_CCITT_POLY = 0x1021
    __CRC_CCITT_INIT = 0xFFFF

    @staticmethod
    def calc_crc(data, crc=None):
        """Calculate CRC16 on the given data."""
        if data is None:
            return None
        if not isinstance(data, bytes) and not isinstance(data, bytearray):
            return None
        if crc is None:
            crc = CRC16.__CRC_CCITT_INIT

        for byte in data:
            crc ^= (byte << 8)
            for _ in range(0, 8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ CRC16.__CRC_CCITT_POLY
                else:
                    crc = (crc << 1)
            crc &= 0xFFFF
        return crc
