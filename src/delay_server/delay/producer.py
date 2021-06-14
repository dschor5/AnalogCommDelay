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

        # Get logger
        logger = logging.getLogger(self.__class__.__name__)

        # Receive the message header
        raw_hdr = sock.recv(SocketServer.HEADER_SIZE)

        # If it does not receive anything, then return None.
        if not raw_hdr:
            return None

        # If the message is incomplete, log a warning and discard. 
        if len(raw_hdr) < SocketServer.HEADER_SIZE:
            logger.warning('Incomplete message header %s', str(raw_hdr))
            return None

        # Unpack the header. 
        msg_hdr = struct.unpack(SocketServer._HEADER_DEF, raw_hdr)

        # Validate message length. 
        if int(msg_hdr[0]) > 1024:
            logger.warning('Invalid message length %d', msg_hdr[0])
            return None

        raw_data = sock.recv(msg_size[0])
        raw_ftr = sock.recv(SocketServer.FOOTER_SIZE)

        crc = CRC16.calc_crc(raw_hdr)
        crc = CRC16.calc_crc(raw_data, crc)

        msg_crc = struct.unpack(SocketServer._FOOTER_DEF, raw_ftr)
        if crc != msg_crc[0]:
            self._logger.warning("CRC %04x != %04x", crc, msg_crc[0])
            return None

        return raw_data

    def run(self, **kwargs): #p_sock, p_stop, p_queue, p_connections):
        """ Thread """

        logger = logging.getLogger(self.__class__.__name__)

        # Validate required kwargs parameters.
        if 'sock' not in kwargs:
            logger.critical("run() missing 'sock'")
            return
        if 'stop' not in kwargs:
            logger.critical("run() missing 'stop'")
            return
        if 'queue' not in kwargs:
            logger.critical("run() missing 'queue'")
            return
        if 'connections' not in kwargs:
            logger.critical("run() missing 'connections'")
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
                    msg = ProducerThread._receive(i_sock)
                    if msg is not None:
                        kwargs['queue'].push(msg)
                        i += 1
            for i_sock in sock_exception:
                print(f"Removing {i_sock}")
                kwargs['connections'].remove(i_sock)

        logger.debug('Produced %d msgs', i)
