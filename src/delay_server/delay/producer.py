""" Producer thread. Receives messages and puts them in a queue. """
import threading
import struct
import select

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
        raw_hdr = sock.recv(SocketServer.HEADER_SIZE)
        if not raw_hdr:
            return None
        msg_size = struct.unpack(SocketServer._HEADER_DEF, raw_hdr)
        if int(msg_size[0]) > 1024:
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

    def run(self, p_sock, p_stop, p_queue, p_connections):
        """ Thread """
        i = 0
        while not p_stop.isSet():
            sock_read, _, sock_exception = select.select(p_connections, [], \
                p_connections, SocketServer._SOCKET_TIMEOUT)
            for i_sock in sock_read:
                # Accept new connections
                if i_sock is p_sock:
                    i_client_socket, i_client_address = p_sock.accept()
                    p_connections.append(i_client_socket)
                    self._logger.info('New connection from %s', i_client_address)
                else:
                    msg = self._receive(i_sock)
                    if msg is not None:
                        p_queue.push(msg)
                        i += 1
            for i_sock in sock_exception:
                print(f"Removing {i_sock}")
                p_connections.remove(i_sock)

        self._logger.debug('Produced %d msgs', i)
