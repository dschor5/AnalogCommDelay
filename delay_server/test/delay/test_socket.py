#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import socket
import mock
import struct
import os
import sys
import logging

# pylint: disable=E0401
from test.test_custom_class import TestClass
from delay_server.delay.socket import DelayServerSocket
from delay_server.util.exceptions import *


class TestSocketServer(TestClass):
    """Test class for main file."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._address = ('', 1000)

    def test_init(self):
        # Test constructor
        sock = DelayServerSocket()
        self.assertIsNotNone(sock)

        # Test socket with non-default logger.
        logger = logging.getLogger('test')
        sock = DelayServerSocket(logger)
        self.assertIsNotNone(sock)

    def test_open(self):
        sock = DelayServerSocket()
        
        # Invalid param address
        with self.assertRaises(AttributeError):
            sock.open(address=None)
        with self.assertRaises(TypeError):
            sock.open(address=1)
        
        # Invalid param timeout
        with self.assertRaises(TypeError):
            sock.open(address=self._address, timeout="test")
        
        # Valid address with default timeout
        sock.open(self._address)
        self.assertIsNotNone(sock._sock)
        self.assertEqual(sock._TIMEOUT, DelayServerSocket._TIMEOUT)
        sock.close()
        
        # Valid address. Override timeout
        sock = DelayServerSocket()
        sock.open(self._address, 5)
        self.assertIsNotNone(sock._sock)
        self.assertEqual(sock._TIMEOUT, DelayServerSocket._TIMEOUT)
        self.assertEqual(sock._sock.gettimeout(), 5)
        sock.close()        

    def test_close(self):
        pass
    

    # def test_receive(self):
    #     sock = DelaySocket()

    #     mock_recv = mock.Mock()
    #     mock_struct = mock.Mock()

    #     # Invalid sock object.
    #     self.assertIsNone(sock.recv_msg(None))

    #     # No message header received
    #     mock_recv.recv.return_value = 0
    #     self.assertIsNone(sock.recv_msg(mock_recv))

    #     # Message header with invalid length.
    #     mock_recv.recv.side_effect = [b'\xFF\xFF']
    #     self.assertIsNone(self.__server._receive(mock_recv))

    #     # Message header with valid length, but invalid length.
    #     mock_recv.recv.side_effect = [b'\x00\x00\x00\x01', 0]
    #     self.assertIsNone(self.__server._receive(mock_recv))

    #     # Failed to parse header
    #     mock_struct.side_effect = struct.error()
    #     mock_recv.recv.side_effect = [b'\x00\x00\x00\x01', 0]
    #     with mock.patch('struct.unpack', mock_struct):
    #         self.assertIsNone(self.__server._receive(mock_recv))

    #     # Invalid message length.
    #     mock_recv.recv.side_effect = [b'\xFF\xFF\xFF\xFF', 0]
    #     self.assertIsNone(self.__server._receive(mock_recv))

    #     # Message data with invalid length.
    #     mock_recv.recv.side_effect = [b'\x00\x00\x00\x03', b'\x01']
    #     self.assertIsNone(self.__server._receive(mock_recv))

    #     # Failed to parse data
    #     mock_struct.side_effect = [(3,), struct.error()]
    #     mock_recv.recv.side_effect = [b'\x00\x00\x00\x03', b'\x00\x00\x00']
    #     with mock.patch('struct.unpack', mock_struct):
    #         self.assertIsNone(self.__server._receive(mock_recv))

    #     # Wrong CRC
    #     mock_recv.recv.side_effect = [b'\x00\x00\x00\x03', b'\x01\x00\x00']
    #     self.assertIsNone(self.__server._receive(mock_recv))

    #     # Valid message (short)
    #     mock_recv.recv.side_effect = [b'\x00\x00\x00\x03', b'\x01\x54\x7E']
    #     ret = self.__server._receive(mock_recv)
    #     self.assertIsNotNone(ret)
    #     self.assertEqual(ret, b'\x01')

    def test_send(self):
        sock = DelayServerSocket()
        sock.open(self._address)
        mock_send = mock.Mock()
        mock_struct = mock.Mock()
        msg = bytearray()

        # raw_data = None
        with self.assertRaises(AttributeError):
            sock._send_packet(sock._sock, None)

        # raw_data is not bytes or bytearray object
        with self.assertRaises(TypeError):
            sock._send_packet(sock._sock, 1)

        # raw_data is invalid length
        raw_data = b'\x01' * (DelayServerSocket.MAX_MSG_LEN + 10)
        with self.assertRaises(SocketSendPktInvalidLength):
            sock._send_packet(sock._sock, raw_data)
        
        # self.assertIsNone(sock.send_msg(None))
        # self.assertIsNone(self.__server._send(mock_send, None))
        # self.assertIsNone(self.__server._send(mock_send, b'\x01'))

        # # Invalid message length
        # msg = bytearray()
        # self.assertIsNone(self.__server._send(mock_send, msg))
        # msg = bytearray(os.urandom(SocketServer.MAX_MSG_LEN))
        # self.assertIsNone(self.__server._send(mock_send, msg))

        # # Failed to parse message header
        # msg = bytearray(b'\x01\x02\x03')
        # mock_struct.side_effect = [struct.error(), struct.error()]
        # with mock.patch('struct.pack', mock_struct):
        #     self.assertIsNone(self.__server._send(mock_send, msg))

        # # Failed to parse message crc
        # msg = bytearray(b'\x01\x02\x03')
        # mock_struct.side_effect = [b'\x00\x00\x00\x03', struct.error()]
        # with mock.patch('struct.pack', mock_struct):
        #     self.assertIsNone(self.__server._send(mock_send, msg))

        # # Failed to send full message
        # msg = bytearray(b'\x01')
        # mock_struct.side_effect = [b'\x00\x00\x00\x03', b'\x54\x7E']
        # mock_send.send.side_effect = [1]
        # with mock.patch('struct.pack', mock_struct):
        #     self.assertIsNone(self.__server._send(mock_send, msg))

        # # Sent full message
        # msg = bytearray(b'\x01')
        # mock_struct.side_effect = [b'\x00\x00\x00\x03', b'\x54\x7E']
        # mock_send.send.side_effect = [7]
        # with mock.patch('struct.pack', mock_struct):
        #     self.assertEqual(self.__server._send(mock_send, msg), 7)

    @unittest.skipIf(sys.platform.startswith("win"),
                      "Will not work on Windows")
    def test_socketpair(self):
        sock = DelayServerSocket()
        # Create a socket pair
        sock_send, sock_recv = socket.socketpair()

        for num_bytes in range(1, DelayServerSocket.MAX_MSG_LEN -
                                DelayServerSocket.FOOTER_SIZE + 1):
            num_bytes = 1
            raw_msg = bytearray(os.urandom(num_bytes))
            msg_len = len(raw_msg) + DelayServerSocket.HEADER_SIZE + \
                DelayServerSocket.FOOTER_SIZE
            self.assertEqual(sock._send_packet(sock_send, raw_msg), msg_len)
            ret = sock._recv_packet(sock_recv)
            self.assertEqual(raw_msg, ret)
        sock_recv.close()
        sock_send.close()
