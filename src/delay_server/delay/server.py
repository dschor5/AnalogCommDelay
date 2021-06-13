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
        threading.Thread.__init__(self)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.info('Create logger "%s"', self.__class__.__name__)

        self._thread_name = p_name

        self._sock_param = dict(host=None, ip=None, port=p_port)

        self._thread_param = dict()
        self._thread_param['sock']  = None
        self._thread_param['stop']  = threading.Event()
        self._thread_param['queue'] = p_queue
        self._thread_param['connections'] = []
        self._thread = None

    @staticmethod
    def _get_host():
        """ Get its own IP address. """
        return requests.get('http://api.apify.org').text

    @staticmethod
    def create_socket(port):
        """ Create socket and start listening for connections. """
        if port is None:
            return None
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', port))
        sock.listen()
        return sock

    @property
    def server_name(self):
        return self._thread_name

    def stop_thread(self, timeout=None):
        """ Set flag to stop thread. """
        self._logger.info('Stop tread')
        self._thread_param['stop'].set()
        # TODO: Wait until the thread joins, then close the socket.
        self._thread = None
        return True

    def start_thread(self):
        """ Start thread. """

        # Only one instance of thread can be active.
        if self._thread is not None:
            return False

        # Ensure the stop parameter is clear.
        self._thread_param['stop'].clear()

        # Create a new socket.
        self._thread_param['sock'] = SocketServer.create_socket(self._sock_param['port'])

        # Start listening for connections.
        self._logger.info('Listening on port %d', self._sock_param['port'])
        self._thread_param['connections'].append(self._thread_param['sock'])

        # Create the thread object
        self._thread = threading.Thread(name=self._thread_name, \
            target=self.run, kwargs=self._thread_param, daemon=True)

        # Start the thread
        self._thread.start()
        self._logger.info('Start thread')

        return True

    @abc.abstractmethod
    def run(self, **kwargs):
        pass
