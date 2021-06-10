""" Abstract socket server. """
import abc
import threading
import struct
import socket
import logging
import requests


class SocketServer(abc.ABC, threading.Thread):
    """ Abstract Socket Server thread. """
    # https://steelkiwi.com/blog/working-tcp-sockets/

    _HEADER_DEF = '! I'
    HEADER_SIZE = struct.calcsize(_HEADER_DEF)

    _FOOTER_DEF = '! H'
    FOOTER_SIZE = struct.calcsize(_FOOTER_DEF)

    _SOCKET_TIMEOUT = 0.01

    def __init__(self, p_name, p_port, p_queue):
        """ Initialize """
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.info('Create logger "%s"', self.__class__.__name__)
        self._name = p_name
        self._sock = dict(host=None, ip=None, port=p_port, sock=None)
        self._thread = None
        self._queue = p_queue
        self._stop = threading.Event()
        self._connections = []
        threading.Thread.__init__(self)
        self.start_thread()

    @staticmethod
    def _get_host():
        """ Get its own IP address. """
        return requests.get('http://api.apify.org').text

    @staticmethod
    def create_socket(port):
        """ Create socket and start listening for connections. """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', port))
        sock.listen()
        return sock

    def stop_thread(self):
        """ Set flag to stop thread. """
        self._logger.info('Stop tread')
        self._stop.set()

    def start_thread(self):
        """ Start thread. """
        if self._thread is not None:
            return
        self._stop.clear()
        self._sock['sock'] = SocketServer.create_socket(self._sock['port'])
        self._sock['host'] = self._sock['sock'].gethostbyname(socket.gethostname())
        self._sock['ip'] = SocketServer._get_host()
        self._logger.info('Listening on port %d', self._sock['port'])
        self._connections.append(self._sock)
        self._thread = threading.Thread(name=self._name, \
            target=self.run, args=(self._sock, self._stop, self._queue, self._connections))
        self._thread.setDaemon(True)
        self._thread.start()
        self._logger.info('Start thread')

    @abc.abstractmethod
    def run(self, p_sock, p_stop, p_queue, p_connections):
        pass
