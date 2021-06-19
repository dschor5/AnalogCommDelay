"""Abstract socket server."""
import abc
import threading
import struct
import socket
import logging

# TODO: Convert code for bytearray (mutable) instead of bytes (immutable)

from common.crc16 import CRC16


class SocketServer(abc.ABC, threading.Thread):
    """Abstract Socket Server thread."""

    # https://steelkiwi.com/blog/working-tcp-sockets/

    _HEADER_DEF = '! I'
    HEADER_SIZE = struct.calcsize(_HEADER_DEF)

    _FOOTER_DEF = '! H'
    FOOTER_SIZE = struct.calcsize(_FOOTER_DEF)

    MAX_MSG_LEN = 1024

    _SOCKET_TIMEOUT = 0.01

    def __init__(self, p_name, p_port, p_queue):
        """Initialize."""
        threading.Thread.__init__(self)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.info('Create logger "%s"', self.__class__.__name__)

        self._thread_name = p_name

        self._sock_port = p_port

        self._thread_param = dict()
        self._thread_param['sock'] = None
        self._thread_param['stop'] = threading.Event()
        self._thread_param['queue'] = p_queue
        self._thread_param['connections'] = []
        self._thread = None

    @staticmethod
    def create_socket(port, timeout=0.1):
        """Create socket and start listening for connections."""
        if port is None:
            return None
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(timeout)
        sock.bind(('', port))
        sock.listen()

        return sock

    @property
    def server_name(self):
        """Accessor for server name."""
        return self._thread_name

    def stop_thread(self, timeout=0.1):
        """Set flag to stop thread."""
        self._logger.info('Stop tread')
        self._thread_param['stop'].set()
        if self._thread is None:
            return False
        self._thread.join(timeout)
        if self._thread.is_alive():
            return False
        self._thread_param['sock'].close()
        self._thread = None
        return True

    def start_thread(self):
        """Start thread."""
        # Only one instance of thread can be active.
        if self._thread is not None:
            return False

        # Ensure the stop parameter is clear.
        self._thread_param['stop'].clear()

        # Create a new socket.
        self._thread_param['sock'] = \
            SocketServer.create_socket(self._sock_port)

        # Start listening for connections.
        self._logger.info('Listening on port %d', self._sock_port)
        self._thread_param['connections'].append(self._thread_param['sock'])

        # Create the thread object
        self._thread = threading.Thread(name=self._thread_name,
                                        target=self.run,
                                        kwargs=self._thread_param,
                                        daemon=True)

        # Start the thread
        self._thread.start()
        self._logger.info('Start thread')

        return True

    def _send(self, sock, raw_data):
        """Send a message."""
        # Disable pylint warning for "Too many return statements"
        # pylint: disable=R0911

        if sock is None or raw_data is None:
            return None

        logger = logging.getLogger(self.__class__.__name__)

        if not isinstance(raw_data, bytearray):
            logger.warning('Wrong msg type')
            return None

        msg_len = len(raw_data) + SocketServer.FOOTER_SIZE
        if msg_len > SocketServer.MAX_MSG_LEN:
            logger.warning('Msg too long')
            return None
        if msg_len == SocketServer.FOOTER_SIZE:
            logger.warning('Msg is empty')
            return None

        try:
            raw_hdr = bytearray(struct.pack(
                SocketServer._HEADER_DEF, msg_len))
            raw_msg = raw_hdr + raw_data
            calc_crc = CRC16.calc_crc(raw_msg)
            raw_ftr = bytearray(struct.pack(
                SocketServer._FOOTER_DEF, calc_crc))
        except struct.error:
            logger.warning('Msg parse error')
            return None

        raw_msg += raw_ftr
        bytes_sent = sock.send(raw_msg)
        if bytes_sent < msg_len:
            logger.warning('Partial message sent')
            return None

        return bytes_sent

    def _receive(self, sock):
        """Receive a message."""
        # Disable pylint warning for "Too many return statements"
        # pylint: disable=R0911

        if sock is None:
            return None

        raw_hdr = sock.recv(SocketServer.HEADER_SIZE)

        # Check for empty message header
        if not raw_hdr:
            return None

        logger = logging.getLogger(self.__class__.__name__)

        # Check for incomplete message header
        if len(raw_hdr) < SocketServer.HEADER_SIZE:
            logger.warning('MsgHdr len=%d < exp=%d',
                           len(raw_hdr), SocketServer.HEADER_SIZE)
            return None

        # Parse message header
        try:
            # Unpack the header.
            msg_hdr = struct.unpack(SocketServer._HEADER_DEF, raw_hdr)
            # Extract message length
            msg_size = int(msg_hdr[0])
        except struct.error:
            logger.warning('MsgHdr parse error')
            return None

        # Validate message length
        if msg_size > SocketServer.MAX_MSG_LEN:
            logger.warning('MsgData invalid len=%d', msg_size)
            return None

        # Get message data
        raw_data = sock.recv(msg_size)

        # Check for empty message data
        if not raw_data:
            logger.warning('MsgData is empty')
            return None

        # Check for incomplete message data
        if len(raw_data) < msg_size:
            logger.warning('MsgData len=%d < exp=%d', len(raw_data), msg_size)
            return None

        # Parse message data/footer
        try:
            struct_def = '! ' + str(msg_size-SocketServer.FOOTER_SIZE) + 's H'
            msg_data = struct.unpack(struct_def, raw_data)
            msg_crc = msg_data[1]
        except struct.error:
            logger.warning('MsgData parse error')
            return None

        calc_crc = CRC16.calc_crc(raw_hdr)
        calc_crc = CRC16.calc_crc(msg_data[0], calc_crc)

        if calc_crc != msg_crc:
            self._logger.warning("Msg CRC recv=%04x != exp=%04x",
                                 msg_crc, calc_crc)
            return None

        # Returns mutable bytearray
        return bytearray(raw_data[:-2])

    def _validate_thread_param(self, **kwargs):
        """Validate thread parameters."""
        req_kwargs = set(['sock', 'stop', 'queue', 'connections'])
        found = req_kwargs.difference(kwargs)
        if len(found) > 0:
            logger = logging.getLogger(self.__class__.__name__)
            logger.critical('run() missing [%s] kwargs', found)
            return False
        return True

    @abc.abstractmethod
    def run(self, **kwargs):
        """Abstract run method for thread."""
        pass
