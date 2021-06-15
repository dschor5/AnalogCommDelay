""" Test for delay.queue module. """
import unittest
import time
import mock
import struct
import random
import os

# Disable pylint warning for import errors. 
# pylint: disable=E0401
from test.test_class import TestClass
from delay.producer import ProducerThread
from delay.queue import DelayQueue
from common.crc16 import CRC16

class TestProducer(TestClass):
    """Test class for main file."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__port = 1000
        self.__queue = DelayQueue()
        self.__server = None
        
    def setUp(self):
        self.__server = ProducerThread(self.__port, self.__queue)

    def tearDown(self):
        if self.__server is not None:
            self.__server.stop_thread()
            self.__server = None

    def test_run(self):
        # Needed for code coverage only. 
        self.__server.run(**dict())
        self.__server.stop_thread()

    def test_receive(self):

        mock_recv = mock.Mock()
        mock_struct = mock.Mock()

        # Invalid sock object. 
        self.assertIsNone(self.__server._receive(None))

        # No message header received
        mock_recv.recv.return_value = 0
        self.assertIsNone(self.__server._receive(mock_recv))

        # Message header with invalid length. 
        mock_recv.recv.side_effect = [b'\xFF\xFF']
        self.assertIsNone(self.__server._receive(mock_recv))

        # Message header with valid length, but invalid length. 
        mock_recv.recv.side_effect = [b'\x00\x00\x00\x01', 0]
        self.assertIsNone(self.__server._receive(mock_recv))

        # Failed to parse header
        mock_struct.side_effect = struct.error()
        mock_recv.recv.side_effect = [b'\x00\x00\x00\x01', 0]
        with mock.patch('struct.unpack', mock_struct):
            self.assertIsNone(self.__server._receive(mock_recv))

        # Invalid message length.
        mock_recv.recv.side_effect = [b'\xFF\xFF\xFF\xFF', 0]
        self.assertIsNone(self.__server._receive(mock_recv))

        # Message data with invalid length. 
        mock_recv.recv.side_effect = [b'\x00\x00\x00\x03', b'\x01']
        self.assertIsNone(self.__server._receive(mock_recv))

        # Failed to parse data
        mock_struct.side_effect = [(3,), struct.error()]
        mock_recv.recv.side_effect = [b'\x00\x00\x00\x03', b'\x00\x00\x00']
        with mock.patch('struct.unpack', mock_struct):
            self.assertIsNone(self.__server._receive(mock_recv))

        # Wrong CRC
        mock_recv.recv.side_effect = [b'\x00\x00\x00\x03', b'\x01\x00\x00']
        self.assertIsNone(self.__server._receive(mock_recv))

        # Valid message (short)
        mock_recv.recv.side_effect = [b'\x00\x00\x00\x03', b'\x01\x54\x7E']
        ret = self.__server._receive(mock_recv)
        self.assertIsNotNone(ret)
        self.assertEqual(ret, b'\x01')

        # Valid message (long)
        raw_hdr = b'\x00\x00\x04\x00'
        raw_data = []
        raw_data.append(b'\x03' * 1022)
        crc = CRC16.calc_crc(raw_hdr)
        crc = CRC16.calc_crc(raw_data[0], crc)
        raw_data.append(crc.to_bytes(2, byteorder='big'))
        msg = b''.join(raw_data)
        mock_recv.recv.side_effect = [raw_hdr, msg]
        ret = self.__server._receive(mock_recv)
        self.assertIsNotNone(ret)
        self.assertEqual(ret, raw_data[0])

        # Valid message with random data(long)
        raw_hdr = b'\x00\x00\x04\x00'
        raw_data = []
        raw_data.append(os.urandom(1022))
        crc = CRC16.calc_crc(raw_hdr)
        crc = CRC16.calc_crc(raw_data[0], crc)
        raw_data.append(crc.to_bytes(2, byteorder='big'))
        msg = b''.join(raw_data)
        mock_recv.recv.side_effect = [raw_hdr, msg]
        ret = self.__server._receive(mock_recv)
        self.assertIsNotNone(ret)
        self.assertEqual(ret, raw_data[0])
