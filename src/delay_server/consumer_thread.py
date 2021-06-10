""" Producer thread. Receives messages and puts them in a queue. """
import threading
#import struct
#import select

from src.delay_server.socket_server import SocketServer
#from src.util.crc16 import CRC16

class ConsumerThread(SocketServer, threading.Thread):
    """ Consumer Thread """

    def __init__(self, p_port, p_queue):
        """ Initializer """
        SocketServer.__init__(self, "Consumer", p_port, p_queue)
        threading.Thread.__init__(self)

    def _send(self, data: bytearray):
        """ Send data """


    def run(self, p_sock, p_stop, p_queue, p_connections):
        """ Thread """
        i = 0
        while not p_stop.isSet():
            data = p_queue.pop()
            if data is not None:
                i += 1
        self._logger.debug('Consumed %d msgs', i)
