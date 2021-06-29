#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import queue


class QueueLogHandler(logging.Handler):
    """Log handler that saves messages to a therad-safe queue.

    Place log messages into a thread-safe queue so that they can be extracted
    from the graphical user interface.
    """

    def __init__(self, log_queue: queue.Queue):
        """Initialize QueueLogHandler with a queue provided by the user.

        Args:
            log_queue (queue.Queue): Queue to use to store messages.
        """
        super().__init__()
        self._queue = log_queue

    def emit(self, record: logging.LogRecord) -> None:
        """Add new entries to the log.

        Args:
            new_record (logging.LogRecord): Log entry to add to the log.
        """
        self._queue.put(record)
