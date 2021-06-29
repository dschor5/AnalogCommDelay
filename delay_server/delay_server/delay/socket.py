"""Abstract socket server."""
import abc
import threading
import struct
import logging
import socket
import select
import traceback

# TODO: Convert code for bytearray (mutable) instead of bytes (immutable)

from delay_server.util.crc16 import CRC16
from delay_server.util.exceptions import *


class DelayServerSocket:
    """Extends socket class and implements packet communication protocol.

    This class enforces the packet structure shown below:
        
    +----------------+----------------------------------+-----------+
    | Primary Header | Packet Data                      | Footer    |
    +----------------+----------------------------------+-----------+
    | Length         | Optional Secondary Header + Data | CRC16     |
    | (2 bytes)      | (1-1020 bytes)                   | (2 bytes) |
    +----------------+----------------------------------+-----------+
    """

    # https://steelkiwi.com/blog/working-tcp-sockets/

    _HEADER_DEF = '! I'
    HEADER_SIZE = struct.calcsize(_HEADER_DEF)

    _FOOTER_DEF = '! H'
    FOOTER_SIZE = struct.calcsize(_FOOTER_DEF)

    MAX_MSG_LEN = 1024

    _TIMEOUT = 0.01

    def __init__(self, logger: logging.Logger = None):
        """Initialize.
        
        Args:
            logger (logging.Logger): Logger associated with parent class.
        """
        # Socket object embedded within this class. 
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # If no logger provided, use a default with the class name. 
        self._logger = logger
        if logger is None:
            self._logger = logging.getLogger(self.__class__.__name__)
            
        # List of connections associated with this socket.
        self._connections = [self._sock]

    def open(self, address: tuple, timeout: int = None):
        """Start listening for connections on the server socket.

        Args:
            address (tuple): Tuple containing IP address and port.
                For example ('127.0.0.1', 1000).
            timeout (int): Timeout for socket operations. Use 0 for blocking.

        Raises:
            socket.error: Error binding to port.
        """
        if address is None:
            raise AttributeError("Socket address cannot be None.")

        if not isinstance(address, tuple):
            raise TypeError("Socket address is invalid.")
        
        if timeout is not None and not isinstance(timeout, (int, float)):
            raise TypeError("Socket timeout is invalid.")
        
        # Only change timeout for this instance.
        if timeout is None:
            timeout = self._TIMEOUT
            
        # Set socket parameters and start listening.
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Setting the timeout also makes this a non-blocking socket.
        self._sock.settimeout(timeout)
        self._sock.bind(address)
        self._sock.listen()
        self._logger.info("Listening on port %s", address)
        
    def close(self):
        """Shutdown and close the socket. 
        
        Catches socket errors and reports them in the log. 
        """
        try:
            if len(self._connections) > 1:
                self._sock.shutdown(socket.SHUT_RDWR)
            self._sock.close()
        except OSError as e:
            self._logger.error(e)
            traceback.print_exc()
        self._logger.info("Closed port.")

    def _send_packet(self, sock: socket.socket, raw_data: bytearray) -> int:
        """Assemble a packet and send it.

        Args:
            raw_data (bytearray): Data.

        Returns:
            int: Number of bytes sent.

        Raises:
            AttributeError: raw_data is None.
            TypeError: raw_data is not :class:`bytearray` or :class:`bytes`.
            SocketSendEmptyPkt: raw_data length cannot be zero.
            SocketSendPktInvalidLength: raw_data exceeds allowed pkt length.
            struct.error: Cannot create struct to build bytearray packet.
        """
        if raw_data is None:
            raise AttributeError("Socket send data cannot be None.")

        if not isinstance(raw_data, (bytes, bytearray)):
            raise TypeError("Socket send data must be a bytes or bytearray.")

        if not len(raw_data):
            raise SocketSendEmptyMessage()

        # Calculate message length including packet footer.
        msg_len = len(raw_data) + self.FOOTER_SIZE
        if msg_len > self.MAX_MSG_LEN:
            raise SocketSendPktInvalidLength()

        # Throws struct.error if it cannot assemble the message.
        raw_hdr = bytearray(struct.pack(self._HEADER_DEF, msg_len))

        # Calc CRC on packet header + body
        calc_crc = CRC16.calc_crc(raw_hdr)
        calc_crc = CRC16.calc_crc(raw_data, calc_crc)

        # Throws struct.error if it cannot assemble the message.
        raw_ftr = bytearray(struct.pack(self._FOOTER_DEF, calc_crc))

        # Concatenate message header, body, and data
        raw_pkt = raw_hdr + raw_data + raw_ftr
        bytes_sent = sock.send(raw_pkt)
        if bytes_sent < msg_len:
            self._logger.warning('Partial message sent')

        return bytes_sent
    
    def accept_and_send(self):
        msg = None
        sock_read, _, sock_exception = \
            select.select(self._connections, [],
                          self._connections,
                          self._TIMEOUT)
        for i_sock in sock_read:
            # Accept new connections to receive messages
            if i_sock is self._sock:
                i_client_socket, i_client_address = self._sock.accept()
                self._connections.append(i_client_socket)
                self._logger.info('New connection from %s', i_client_address)
            else:
                msg = self._recv_packet(i_sock)
        for i_sock in sock_exception:
            print(f"Removing {i_sock}")
            self._connections.remove(i_sock)
        return msg    

    def _recv_packet(self, sock: socket.socket):
        """Receive a message."""

        raw_hdr = sock.recv(self.HEADER_SIZE)

        # Check for empty message header
        if not raw_hdr:
            return None

        # Check for incomplete message header
        if len(raw_hdr) < self.HEADER_SIZE:
            self._logger.warning('MsgHdr len=%d < exp=%d',
                           len(raw_hdr), self.HEADER_SIZE)
            return None

        # Parse message header
        try:
            # Unpack the header.
            msg_hdr = struct.unpack(self._HEADER_DEF, raw_hdr)
            # Extract message length
            msg_size = int(msg_hdr[0])
        except struct.error:
            self._logger.warning('MsgHdr parse error')
            return None

        # Validate message length
        if msg_size > self.MAX_MSG_LEN:
            self._logger.warning('MsgData invalid len=%d', msg_size)
            return None

        # Get message data
        raw_data = sock.recv(msg_size)

        # Check for empty message data
        if not raw_data:
            self._logger.warning('MsgData is empty')
            return None

        # Check for incomplete message data
        if len(raw_data) < msg_size:
            self._logger.warning('MsgData len=%d < exp=%d',
                                 len(raw_data), msg_size)
            return None

        # Parse message data/footer
        try:
            struct_def = '! ' + str(msg_size-self.FOOTER_SIZE) + 's H'
            msg_data = struct.unpack(struct_def, raw_data)
            msg_crc = msg_data[1]
        except struct.error:
            self._logger.warning('MsgData parse error')
            return None

        calc_crc = CRC16.calc_crc(raw_hdr)
        calc_crc = CRC16.calc_crc(msg_data[0], calc_crc)

        if calc_crc != msg_crc:
            self._logger.warning("Msg CRC recv=%04x != exp=%04x",
                                 msg_crc, calc_crc)
            return None

        # Returns mutable bytearray
        return bytearray(raw_data[:-2])

    def accept_and_recv(self):
        """Accept new connections and receive packets."""
        msg = None
        sock_read, _, sock_exception = \
            select.select(self._connections,
                          [],
                          self._connections,
                          self._TIMEOUT)
        for i_sock in sock_read:
            # Accept new connections to receive messages
            if i_sock is self._sock:
                i_client_socket, i_client_address = self._sock.accept()
                self._connections.append(i_client_socket)
                self._logger.info('New connection from %s', i_client_address)
            else:
                msg = self._recv_packet(i_sock)
        for i_sock in sock_exception:
            print(f"Removing {i_sock}")
            self._connections.remove(i_sock)
        return msg
