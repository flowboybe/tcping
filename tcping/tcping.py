#!/usr/bin/env python3

import socket
import struct
import argparse
import time


def build_header(source_port, dest_port):
    # Простейший TCP-заголовок (20 байт)
    seq = 52
    ack_seq = 0
    doff_reserved = (5 << 4)  # data offset (5 x 4 = 20 байт), без опций
    flags = 2  # SYN
    window = socket.htons(5840)  # размер окна
    checksum = 0  # временно 0, позже можно посчитать
    urg_ptr = 0

    # Пакуем заголовок
    tcp_header = struct.pack('!HHLLBBHHH',
        source_port,      # Source port
        dest_port,        # Destination port
        seq,              # Sequence number
        ack_seq,          # Acknowledgement number
        doff_reserved,    # Data offset + reserved
        flags,            # TCP flags
        window,           # Window size
        checksum,         # Checksum
        urg_ptr           # Urgent pointer
    )

    return tcp_header


parser = argparse.ArgumentParser()
parser.add_argument('host')
parser.add_argument('port')
args = parser.parse_args()
ip = socket.gethostbyname(args.host)
port = int(args.port)

sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
header = build_header(52525, port)
while True:
    time.sleep(1)
    sock.sendto(header, (ip, port))
    print('пинганул')