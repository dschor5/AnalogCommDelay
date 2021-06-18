""" Producer thread. Receives messages and puts them in a queue. """
import select
import logging

from delay.server import SocketServer
# pylint: disable=R0801
class ProducerThread(SocketServer):
    """ Receive messages. Put them in the queue."""

    def __init__(self, p_port, p_queue):
        """ Initializer. """
        SocketServer.__init__(self, "Producer", p_port, p_queue)

    def run(self, **kwargs):
        """ Thread """

        logger = logging.getLogger(self.__class__.__name__)
        if not self._validate_thread_param(**kwargs):
            return

        i = 0
        while not kwargs['stop'].isSet():
            sock_read, _, sock_exception = select.select(kwargs['connections'], [], \
                kwargs['connections'], SocketServer._SOCKET_TIMEOUT)
            for i_sock in sock_read:
                # Accept new connections to receive messages
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
