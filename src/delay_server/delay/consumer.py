""" Producer thread. Receives messages and puts them in a queue. """
import threading
import logging
#import struct
#import select

from delay.server import SocketServer
#from common.crc16 import CRC16

class ConsumerThread(SocketServer, threading.Thread):
    """ Consumer Thread """

    def __init__(self, p_port, p_queue):
        """ Initializer """
        SocketServer.__init__(self, "Consumer", p_port, p_queue)
        threading.Thread.__init__(self)

    def _send(self, data: bytearray):
        """ Send data """


    def run(self, **kwargs):
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
            data = kwargs['queue'].pop()
            if data is not None:
                i += 1
        logger.debug('Consumed %d msgs', i)
