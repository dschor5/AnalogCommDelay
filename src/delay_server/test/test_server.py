""" Test for delay.queue module. """
import unittest
import socket
import mock
import struct
import random
import os
import sys

# pylint: disable=E0401
from test.test_class import TestClass
from delay.server import SocketServer
from delay.producer import ProducerThread
from delay.queue import DelayQueue
from common.crc16 import CRC16

class TestServer(TestClass):
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

    def test_init(self):

        # Test abstract constructor
        with self.assertRaises(TypeError):
            SocketServer("Test", self.__port, self.__queue)

        # Test constructor
        self.assertIsNotNone(self.__server)

        # Test property name
        self.assertEqual(self.__server.server_name, "Producer")

    def test_create_socket(self):
        self.assertIsNone(SocketServer.create_socket(None))
        if os.environ.get('TRAVISCI') is not None:
            with mock.patch('delay.server.socket.socket.bind'):
                ret = SocketServer.create_socket(1000)
        else:
            ret = SocketServer.create_socket(1000)
        self.assertIsNotNone(ret)
        ret.close()

    def test_thread(self):
        # Mock for socket.bind for travis-ci.
        if os.environ.get('TRAVISCI') is not None:
            with mock.patch('delay.server.socket.socket.bind'):
                self.assertTrue(self.__server.start_thread())
        else:
            self.assertTrue(self.__server.start_thread())

        # Start thread already running. 
        self.assertFalse(self.__server.start_thread())

        # Stop thread nominal.
        self.assertTrue(self.__server.stop_thread())

        # Stp server already off. 
        self.assertFalse(self.__server.stop_thread())

        # Stop a thread fails join. 
        self.__server = ProducerThread(self.__port, self.__queue)
        if os.environ.get('TRAVISCI') is not None:
            with mock.patch('delay.server.socket.socket.bind'):
                self.assertTrue(self.__server.start_thread())
        else:
            self.assertTrue(self.__server.start_thread())

        mock_obj = mock.Mock()
        mock_obj.return_value = True
        with mock.patch('delay.server.threading.Thread.is_alive', mock_obj):
            self.assertFalse(self.__server.stop_thread())

    def test_run(self):
        # Needed for code coverage only. 
        SocketServer.run(dict())

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

    def test_send(self):
        mock_send = mock.Mock()
        mock_struct = mock.Mock()
        msg = bytearray()

        # Invalid params.
        self.assertIsNone(self.__server._send(None, bytearray()))
        self.assertIsNone(self.__server._send(mock_send, None))
        self.assertIsNone(self.__server._send(mock_send, b'\x01'))

        # Invalid message length
        msg = bytearray()
        self.assertIsNone(self.__server._send(mock_send, msg))
        msg = bytearray(os.urandom(SocketServer.MAX_MSG_LEN))
        self.assertIsNone(self.__server._send(mock_send, msg))

        # Failed to parse message header
        msg = bytearray(b'\x01\x02\x03')
        mock_struct.side_effect = [struct.error(), struct.error()]
        with mock.patch('struct.pack', mock_struct):
            self.assertIsNone(self.__server._send(mock_send, msg))

        # Failed to parse message crc
        msg = bytearray(b'\x01\x02\x03')
        mock_struct.side_effect = [b'\x00\x00\x00\x03', struct.error()]
        with mock.patch('struct.pack', mock_struct):
            self.assertIsNone(self.__server._send(mock_send, msg))

        # Failed to send full message
        msg = bytearray(b'\x01')
        mock_struct.side_effect = [b'\x00\x00\x00\x03', b'\x54\x7E']
        mock_send.send.side_effect = [1]
        with mock.patch('struct.pack', mock_struct):
            self.assertIsNone(self.__server._send(mock_send, msg))

        # Sent full message
        msg = bytearray(b'\x01')
        mock_struct.side_effect = [b'\x00\x00\x00\x03', b'\x54\x7E']
        mock_send.send.side_effect = [7]
        with mock.patch('struct.pack', mock_struct):
            self.assertEqual(self.__server._send(mock_send, msg), 7)

    @unittest.skipIf(sys.platform.startswith("win"), "Will not work on Windows")
    def test_socketpair(self):
        print("Running!")
        # Create a socket pair 
        sock_send, sock_recv = socket.socketpair()
        
        for num_bytes in range(1, SocketServer.MAX_MSG_LEN-SocketServer.FOOTER_SIZE+1):
            num_bytes = 1
            raw_msg = bytearray(os.urandom(num_bytes))
            msg_len = len(raw_msg) + SocketServer.HEADER_SIZE + SocketServer.FOOTER_SIZE
            self.assertEqual(self.__server._send(sock_send, raw_msg), msg_len)
            ret = self.__server._receive(sock_recv)
            self.assertEqual(raw_msg, ret)
        sock_recv.close()
        sock_send.close()

