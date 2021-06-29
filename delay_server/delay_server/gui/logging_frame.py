#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import queue
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

from delay_server.util.log_handler import QueueLogHandler


class LoggingFrame:
    """Class sends logging records to a queue that can be retrieved from a GUI.
    """

    def __init__(self, frame):
        self._frame = frame

        self._scrolled_text = ScrolledText(frame,
                                           state='disabled', padx=5, pady=5,
                                           bg='black')

        self._scrolled_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._scrolled_text.configure(font='TkFixedFont')
        self._scrolled_text.tag_config('INFO', foreground='white')
        self._scrolled_text.tag_config('DEBUG', foreground='gray')
        self._scrolled_text.tag_config('WARNING', foreground='yellow')
        self._scrolled_text.tag_config('ERROR', foreground='orange')
        self._scrolled_text.tag_config('CRITICAL', foreground='red')

        # Create a logging handler using a queue
        self._log_queue = queue.Queue()
        self._queue_handler = QueueLogHandler(self._log_queue)
        formatter = logging.Formatter('%(asctime)s: %(message)s')
        self._queue_handler.setFormatter(formatter)
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(self._queue_handler)

    def update(self):
        while True:
            try:
                record = self._log_queue.get(block=False)
            except queue.Empty:
                break
            else:
                self._display(record)

    def _display(self, record: logging.LogRecord) -> None:
        msg = self._queue_handler.format(record)
        self._scrolled_text.configure(state='normal')
        self._scrolled_text.insert(tk.END, '> ' + msg + '\n', record.levelname)
        self._scrolled_text.configure(state='disabled')
        # Automatically scrolls to the bottom.
        self._scrolled_text.yview(tk.END)
