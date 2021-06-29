class CRC16:
    """Implementation of CRC-16 CCITT-FALSE Algorithm."""

    __CRC_CCITT_POLY = 0x1021
    __CRC_CCITT_INIT = 0xFFFF

    @staticmethod
    def calc_crc(data: bytearray, crc: int = None):
        """Calculate CRC16 on the given data.

        Args:
            data (bytes or bytearray): Data to compute CRC on. Cannot be None.
            crc (int): Seed value. If not provided defaults to 0xFFFF.

        Returns:
            int: 16-bit CRC.

        Raises:
            AttributeError: Data is None.
            TypeError: Data is neither a :class:`bytes` or :class:`bytearray`.
        """
        if data is None:
            raise AttributeError("Variable 'data' is None.")

        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("Cannot compute CRC on " + type(data))

        # Use default seed if none is provided.
        if crc is None:
            crc = CRC16.__CRC_CCITT_INIT

        # Compute CRC.
        for byte in data:
            crc ^= (byte << 8)
            for _ in range(0, 8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ CRC16.__CRC_CCITT_POLY
                else:
                    crc = (crc << 1)
            crc &= 0xFFFF

        return crc
