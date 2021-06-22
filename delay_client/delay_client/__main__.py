""" Main application """

import struct
import time
import random
import socket
import os
import logging

# pylint: disable=E0401
from delay_server.delay.delay import CommDelay
from delay_server.delay.queue import DelayQueue
from delay_server.delay.producer import ProducerThread
from delay_server.delay.consumer import ConsumerThread
from delay_server.delay.config import DelayConfig
from delay_server.util.crc16 import CRC16


def test_client():
    """Test client."""
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect(('', 1001))


if __name__ == "__main__":

    logging.basicConfig(format='%(asctime)s:%(name)s:%(levelname)s:%(message)s', \
        filemode='w', level=logging.DEBUG, filename='DelayServer2.log')
    logging.info('Created logger')
    delay = CommDelay().set_override(5)
    config = DelayConfig()

    queue = DelayQueue()
    consumer = ConsumerThread(int(config.get('mcc', 'post_recv')), queue)
    consumer.start_thread()
    producer = ProducerThread(int(config.get('hab', 'port_send')), queue)
    producer.start_thread()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', int(config.get('mcc', 'post_recv'))))
    time.sleep(0.1)
    print("Send packet_data")
    i = 0
    while i < 1:
        num_bytes = random.randint(3, 10)
        packed_data = struct.pack('! I', num_bytes)
        crc = CRC16.calc_crc(packed_data)
        data = os.urandom(num_bytes - 2)
        crc = CRC16.calc_crc(data, crc)
#        if random.randint(1, 100) < 1:
#            crc += 1
        values = (num_bytes, data, crc)
        packer = struct.Struct('! I ' + str(num_bytes-2) + 's H')

        print("Send " + str(values))
        packed_data = packer.pack(*values)
        sock.sendall(packed_data)
        if random.randint(1, 100) < 1:
            time.sleep(0.001)
        i += 1
    print("End of packet_data")
    sock.close()

    time.sleep(10)
    consumer.stop_thread()
    producer.stop_thread()
    time.sleep(2)
