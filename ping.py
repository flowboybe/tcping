import socket
import struct
import time

from packet_manager import send_packet, receive_packet


def ping(src_ip, dst_ip, src_port, dst_port, timeout, interval, count,
         outer_data):  # Отправляет и получает пакеты исходя из параметров
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                      socket.IPPROTO_TCP)  # RAW-socket для ручного формирования TCP, но автоматического IPv4
    s.settimeout(timeout)
    while count:
        seq, start_time = send_packet(s, src_ip, dst_ip, src_port, dst_port)
        outer_data [1] += 1

        receive_packet(s, src_ip, src_port, dst_ip, dst_port, start_time, outer_data, seq)

        count -= 1
        time.sleep(interval)