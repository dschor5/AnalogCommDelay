# -*- coding: utf-8 -*-

import tkinter as tk
import time
import threading
import datetime
import logging

#from delay_sever.delay.config import DelayConfig
from delay_server.gui.logging_frame import LoggingFrame


class ServerApp(tk.Frame):
    """GUI for Delay Emulation Server.
    """

    # Window dimensions in pixels
    _HEIGHT = 600
    _WIDTH = 800

    def __init__(self, root):
        super().__init__(root)
        self._root = root
        self._root.title('Delay Emulation Server')
        self._root.geometry(f'{self._WIDTH}x{self._HEIGHT}')
        self._root.minsize(self._WIDTH, self._HEIGHT)
        self._root.configure(background='black')

        self._date_str = tk.StringVar()
        self._create_widgets()
        self._start_update_threads()

        # Register function to call when closing the application.
        self._root.protocol('WM_DELETE_WINDOW', self._on_close)

    def _on_close(self):
        """Called when closing the application."""
        self._timer.cancel()
        self._root.destroy()

    def _create_widgets(self):
        display_frame = tk.Frame(self._root, width=self._WIDTH, height=300, bg="orange")
        display_frame.pack(fill=tk.BOTH, expand=True)

        stats_frame = tk.Frame(self._root, width=200, height=300, bg="green")
        stats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        log_frame = tk.Frame(self._root, bg="blue")
        log_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._log_frame = LoggingFrame(log_frame)

        met_label = tk.Label(display_frame, text="MET = 2021-06-15 12:34:56")
        met_label.place(relx=0.5, height=20, y=10, anchor="c")

        self._lbl1 = tk.Label(display_frame, textvariable=self._date_str)
        self._lbl1.place(relx=0.5, rely=0.5, anchor="c")

        #button = tk.Button(display_frame, text="Click me!", command=self.do_something)
        #button.place(relx=0.6, rely=0.6, anchor="c")
        
    def _start_update_threads(self):
        self._timer = threading.Timer(1.0, self._update_display)
        self._timer.setDaemon(True)
        self._timer.start()


    def _update_display(self):
        # Catch RuntimeErrors if the application is closed while the 
        # timer is still running.
        try:
            curr_time = datetime.datetime.today()
            curr_time_str = curr_time.strftime('%Y-%m-%d %H:%M:%S')
            self._date_str.set(curr_time_str)
    
            self._log_frame.update()
            logger = logging.getLogger()
            logger.error('ERROR')
            logger.warning('WARNING')
            logger.info('INFO')
            logger.debug('DEBUG')
            logger.critical('CRITICAL')
        except RuntimeError:
            pass
            
        self._timer = threading.Timer(1.0, self._update_display)
        self._timer.setDaemon(True)
        self._timer.start()

if __name__ == '__main__':
    root = tk.Tk()
    app = ServerApp(root)
    app.mainloop()
