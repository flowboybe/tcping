import random
import socket
import struct
import time

from packet_builder import build_packet


def ping(src_ip, dst_ip, src_port, dst_port, timeout, interval, count,
         outer_data):  # Отправляет и получает пакеты исходя из параметров
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                      socket.IPPROTO_TCP)  # RAW-socket для ручного формирования TCP, но автоматического IPv4
    s.settimeout(timeout)
    while count:
        seq = random.randint(1, 10000000)
        tcp_packet = build_packet(src_ip, dst_ip, src_port, dst_port, seq, 2)
        start_time = time.time()
        s.sendto(tcp_packet, (dst_ip, dst_port))
        outer_data [1] += 1

        try:
            while True: # Ждем получение пакета, пока не выйдет время
                response = s.recvfrom(1024)
                if not response: continue
                data, _ = response

                ip_header = data [0:20]  # Распаковка IPv4 заголовка
                iph = struct.unpack('!BBHHHBBH4s4s', ip_header)
                src_ip_packet = socket.inet_ntoa(iph [8])
                dst_ip_packet = socket.inet_ntoa(iph [9])

                tcp_header = data [20:40]  # Распаковка TCP заголовка
                tcph = struct.unpack('!HHLLBBHHH', tcp_header)
                src_port_packet = tcph [0]
                dst_port_packet = tcph [1]
                ack_num = tcph [3]
                flags = tcph [5]

                if (src_ip_packet == dst_ip and dst_ip_packet == src_ip and
                        src_port_packet == dst_port and dst_port_packet == src_port and ack_num == seq + 1):  # Проверка на корректность пакета
                    ack_time = round((time.time() - start_time) * 1000, 2)
                    if (flags & 0x14) == 0x14:  # Проверка на RST + ACK флаг
                        print(f'Порт {dst_port} закрыт.')
                    elif (flags & 0x12) == 0x12:  # Проверка на ACK флаг
                        outer_data [0].append(ack_time)
                        outer_data [2] += 1
                        print(f'Получен пакет от {src_ip_packet}:{src_port_packet}, время = {ack_time}мс')
                    break


        except socket.timeout:  # Если ответ не пришел
            print(f'Запрос на {dst_ip}:{dst_port} - Время истекло')

        count -= 1
        time.sleep(interval)