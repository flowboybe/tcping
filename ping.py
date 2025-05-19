import socket
import time

from packet_manager import send_packet, receive_packet


def ping(src_ip, dst_ip, src_port, dst_port, timeout, interval, count,
         outer_data, version, verbose):  # Отправляет и получает пакеты исходя из параметров
    if version == 4:
        ip_prot = socket.AF_INET
    elif version == 6:
        ip_prot = socket.AF_INET6
    else:
        raise TypeError
    s = socket.socket(ip_prot, socket.SOCK_RAW,
                      socket.IPPROTO_TCP)  # RAW-socket для ручного формирования TCP, но автоматического IPv4
    s.settimeout(timeout)
    while count:
        seq, start_time = send_packet(s, src_ip, dst_ip, src_port, dst_port, version, verbose)
        outer_data [1] += 1

        receive_packet(s, src_ip, src_port, dst_ip, dst_port, start_time, outer_data, seq, version, verbose)

        count -= 1
        time.sleep(interval)