""" Main application """

import struct
import time
import random
import socket
import os
import logging

# pylint: disable=E0401
from delay.config import DelayConfig
from delay.queue import DelayQueue
from delay.producer import ProducerThread
from delay.consumer import ConsumerThread
from common.crc16 import CRC16

if __name__ == "__main__":

    logging.basicConfig(format='%(asctime)s:%(name)s:%(levelname)s:%(message)s', \
        filemode='w', level=logging.DEBUG, filename='DelayServer2.log')
    logging.info('Created logger')
    c = DelayConfig()
    c.set_override(5)

    q = DelayQueue()
    c = ConsumerThread(1000, q)
    p = ProducerThread(1001, q)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 1001))
    time.sleep(0.1)
    print("Send packet_data")
    i = 0
    while i < 10:
        num_bytes = random.randint(1, 3)
        packed_data = struct.pack('! I', num_bytes)
        crc = CRC16.calc_crc(packed_data)
        data = os.urandom(num_bytes)
        crc = CRC16.calc_crc(data, crc)
        if random.randint(1, 100) < 1:
            crc += 1
        values = (num_bytes, data, crc)
        packer = struct.Struct('! I ' + str(num_bytes) + 's H')

        packed_data = packer.pack(*values)
        s.sendall(packed_data)
        if random.randint(1, 100) < 1:
            time.sleep(0.001)
        i += 1
    print("End of packet_data")
    s.close()

    time.sleep(5)
    c.stop_thread()
    p.stop_thread()
    time.sleep(2)
