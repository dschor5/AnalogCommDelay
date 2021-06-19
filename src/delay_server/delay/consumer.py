"""Producer thread. Receives messages and puts them in a queue."""
import logging
import select

from delay.server import SocketServer


class ConsumerThread(SocketServer):
    """Consumer Thread."""

    def __init__(self, p_port, p_queue):
        """Initialize thread."""
        SocketServer.__init__(self, "Consumer", p_port, p_queue)

    def run(self, **kwargs):
        """Thread."""
        logger = logging.getLogger(self.__class__.__name__)

        if not self._validate_thread_param(**kwargs):
            return

        i = 0
        while not kwargs['stop'].isSet():
            sock_read, sock_write, sock_exception = \
                select.select(kwargs['connections'],
                              kwargs['connections'],
                              kwargs['connections'],
                              SocketServer._SOCKET_TIMEOUT)
            for i_sock in sock_read:
                # Accept new connections to send messages
                if i_sock is kwargs['sock']:
                    i_client_socket, i_client_address = kwargs['sock'].accept()
                    kwargs['connections'].append(i_client_socket)
                    logger.info('New connection from %s', i_client_address)
            data = kwargs['queue'].pop()
            if data is not None:
                for i_sock in sock_write:
                    self._send(i_sock, data)
            for i_sock in sock_exception:
                print(f"Removing {i_sock}")
                kwargs['connections'].remove(i_sock)
                i += 1
        logger.debug('Consumed %d msgs', i)
