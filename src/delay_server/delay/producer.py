""" Producer thread. Receives messages and puts them in a queue. """
import threading
import struct
import select
import logging

from delay.server import SocketServer
from common.crc16 import CRC16

class ProducerThread(SocketServer, threading.Thread):
    """ Receive messages. Put them in the queue."""

    def __init__(self, p_port, p_queue):
        """ Initializer. """
        SocketServer.__init__(self, "Producer", p_port, p_queue)
        threading.Thread.__init__(self)

    def _receive(self, sock):
        """ Receive a message. """

        # Disable pylint warning for "Too many return statements"
        # pylint: disable=R0911

        logger = logging.getLogger(self.__class__.__name__)

        if sock is None:
            return None

        raw_hdr = sock.recv(SocketServer.HEADER_SIZE)

        # Check for empty message header
        if not raw_hdr:
            return None

        # Check for incomplete message header
        if len(raw_hdr) < SocketServer.HEADER_SIZE:
            logger.warning('MsgHdr len=%d < exp=%d', len(raw_hdr), SocketServer.HEADER_SIZE)
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
        if msg_size > 1024:
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
            struct_def = '! ' + str(msg_size-2) + 's H'
            msg_data = struct.unpack(struct_def, raw_data)
            msg_crc = msg_data[1]
        except struct.error:
            logger.warning('MsgData parse error')
            return None

        calc_crc = CRC16.calc_crc(raw_hdr)
        calc_crc = CRC16.calc_crc(msg_data[0], calc_crc)

        if calc_crc != msg_crc:
            self._logger.warning("Msg CRC recv=%04x != exp=%04x", msg_crc, calc_crc)
            return None

        return raw_data[:-2]

    def run(self, **kwargs):
        """ Thread """

        logger = logging.getLogger(self.__class__.__name__)
        req_kwargs = set(['sock', 'stop', 'queue', 'connections'])
        found = req_kwargs.difference(kwargs)
        if len(found) > 0:
            logger.critical('run() missing [%s] kwargs', found)
            return

        i = 0
        while not kwargs['stop'].isSet():
            sock_read, _, sock_exception = select.select(kwargs['connections'], [], \
                kwargs['connections'], SocketServer._SOCKET_TIMEOUT)
            for i_sock in sock_read:
                # Accept new connections
                if i_sock is kwargs['sock']:
                    i_client_socket, i_client_address = kwargs['sock'].accept()
                    kwargs['connections'].append(i_client_socket)
                    logger.info('New connection from %s', i_client_address)
                else:
                    msg = self._receive(i_sock)
                    if msg is not None:
                        kwargs['queue'].push(msg)
                        i += 1
            for i_sock in sock_exception:
                print(f"Removing {i_sock}")
                kwargs['connections'].remove(i_sock)

        logger.debug('Produced %d msgs', i)
