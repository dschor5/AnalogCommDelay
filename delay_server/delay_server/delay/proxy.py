#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import time
import threading

from delay_server.util.queue import DelayQueue
from delay_server.delay.socket import DelayServerSocket


class DelayProxy:

    _TIMEOUT = 0.5

    def __init__(self, proxy_name: str):
        self._proxy_name = proxy_name
        self._logger = logging.getLogger(proxy_name)
        self._queue = DelayQueue(self._logger)
        self._producer = None
        self._consumer = None
        self._stop = threading.Event()

    def start_proxy(self, producer_port: int, consumer_port: int) -> None:
        """Start proxy by running the producer and consumer threads.

        Args:
            producer_port (int): Port to receive messages.
            consumer_port (int): Port to send messages.
        """
        # Enable loop in the threads.
        self._stop.clear()

        # Clear shared message queue.
        self._queue.clear()

        # Start consumer thread.
        self._consumer = threading.Thread(
            target=self._run_consumer,
            args=(consumer_port,),
            name=self._proxy_name + "_consumer",
            daemon=True)
        self._consumer.start()

        # Start producer thread.
        self._producer = threading.Thread(
            target=self._run_producer,
            args=(producer_port,),
            name=self._proxy_name + "_producer",
            daemon=True)
        self._producer.start()

    def get_queue_length(self) -> int:
        """Returns the length of the queue."""
        return len(self._queue)

    def stop_proxy(self) -> None:
        """Stop proxy and terminate producer and consumer therads."""
        # Set flag to stop threads.
        self._stop.set()

        # Only applies to active threads.
        if self._producer is not None and self._consumer is not None:
            # Wait to allow threads to complete gracefully.
            time.sleep(self._TIMEOUT)

            # Join threads and destroy objects.
            self._producer.join(self._TIMEOUT)
            self._producer = None
            self._consumer.join(self._TIMEOUT)
            self._consumer = None

    # TODO: Create sockets. If successful, then start the threads.

    def _run_producer(self, port: int) -> None:
        """Procuer Thread. Receive messages and add them to the queue.

        Args:
            port (int): Port used to receive messages.
        """
        # Create and open socket.
        sock = DelayServerSocket(self._logger)
        sock.open(('', port))

        i = 0
        while not self._stop.isSet():
            msg = sock.accept_and_recv()
            if msg is not None:
                self._queue.push(msg)
                i += 1

        self._logger.debug('Produced %d msgs', i)

    def _run_consumer(self, port: int) -> None:
        """Consumer Thread. Take messages from queue and send them to client.

        Args:
            port (int): Port used to send messages.
        """
        sock = DelayServerSocket(self._logger)
        sock.open(('', port))

        i = 0
        while not self._stop.isSet():
            data = self._queue.pop()
            if data is not None:
                #print("Received: " + str(data))
                i += 1

        self._logger.debug('Consumed %d msgs', i)
