#!/usr/bin/python3

import random
import socket
import struct
import time
import argparse


def get_ip(): # Возвращает Ip адрес компьютера пользователя
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    s.connect(('8.8.8.8', 80))
    return s.getsockname() [0]

def calculate_check_sum(msg): # Считает контрольную сумму для пакета
    sum_ = 0
    is_even = len(msg) % 2
    for i in range(0, len(msg) - is_even, 2):
        sum_ += (msg [i]) + ((msg [i + 1]) << 8)
    if is_even:
        sum_ += (msg [len(msg) - is_even + 1])
    while sum_ >> 16:
        sum_ = (sum_ & 0xFFFF) + (sum_ >> 16)
    sum_ = ~sum_ & 0xffff
    return sum_

def parse_args(): # Парсит данные с командной строки
    parser = argparse.ArgumentParser(description='TCP Ping')
    parser.add_argument('host', type=str, help='Ip адрес на который будет отправлен запрос')
    parser.add_argument('-p', '--port', type=int, default=80, help='Порт для пинга, по умолчанию 80')
    parser.add_argument('-w', '--waiting', type=int, default=5, help='Время ожидания ответа, по умолчанию 5 секунд')
    parser.add_argument('-i', '--interval', type=float, default=1, help='Интервал между запросами, по умолчанию 1 секунда')
    parser.add_argument('-n', '--count', type=int, default=float('Inf'), help='Количество запросов, по умолчанию бесконечно')
    args = parser.parse_args()
    return args

def build_packet(src_ip, dst_ip, src_port, dst_port, seq, flags): # Собирает TCP пакет
    packet = struct.pack(
        '!HHIIBBHHH',
        src_port, dst_port, seq, 0, 5 << 4, flags, 1024, 0, 0
    )

    pseudo_hdr = struct.pack(
        '!4s4sHH',
        socket.inet_aton(src_ip), socket.inet_aton(dst_ip), socket.IPPROTO_TCP, len(packet)
    )

    checksum = calculate_check_sum(pseudo_hdr + packet)
    packet = packet [:16] + struct.pack('H', checksum) + packet [18:]

    return packet

def check_free_port(): # Проверяет какой порт свободен на компьюютере отправителя
    for port in range(49152, 65536):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return port
            except socket.error:
                continue
    return None

def ping(src_ip, dst_ip, src_port, dst_port, timeout, interval, count): # Отправляет и получает пакеты исходя из параметров
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP) # RAW-socket для ручного формирования TCP, но автоматического IPv4
    seq = random.randint(1, 10000000)
    times = []
    sent = 0
    received = 0
    while count:
        tcp_packet = build_packet(src_ip, dst_ip, src_port, dst_port, seq, 2)
        start_time = time.time()
        s.sendto(tcp_packet, (dst_ip, dst_port))
        sent += 1

        s.settimeout(timeout)
        try:
            data, _ = s.recvfrom(40)

            ip_header = data [0:20] # Распаковка IPv4 заголовка
            iph = struct.unpack('!BBHHHBBH4s4s', ip_header)
            src_ip_packet = socket.inet_ntoa(iph [8])
            dst_ip_packet = socket.inet_ntoa(iph [9])

            tcp_header = data [20:40] # Распаковка TCP заголовка
            tcph = struct.unpack('!HHLLBBHHH', tcp_header)
            src_port_packet = tcph [0]
            dst_port_packet = tcph [1]
            ack_num = tcph [3]
            flags = tcph [5]
            ack_time = round((time.time() - start_time) * 1000, 2)

            if (src_ip_packet == dst_ip and dst_ip_packet == src_ip and
                    src_port_packet == dst_port and dst_port_packet == src_port and ack_num == seq + 1): # Проверка на корректность пакета
                if (flags == 0x12):# Проверка на SYN/ACK флаг
                    times.append(ack_time)
                    received += 1
                    print(f'Получен пакет от {src_ip_packet}:{src_port_packet}, время = {ack_time}мс')
                elif (flags == 0x04): # Если на SYN запрос пришел флаг RST
                    print('Порт закрыт')

        except socket.timeout: # Если ответ не пришел
            print(f'Запрос на {dst_ip}:{dst_port} - Время истекло')

        count -= 1
        time.sleep(interval)
    return times, sent, received

def main():
    args = parse_args()
    if not args.host[0].isdigit():
        dst_ip = socket.gethostbyname(args.host)
    else:
        dst_ip = args.host
    src_ip = get_ip()
    free_port = check_free_port()
    print(f'Начинаю отправку TCP пакетов на {dst_ip}:{args.port} от {src_ip}:{free_port}')
    data = ping(src_ip, dst_ip, free_port, args.port, args.waiting, args.interval, args.count)
    print(f'Отправлено {data[1]} пакетов, получено {data[2]} пакетов, процент потерь - {int((1 - data[2]/data[1])*100)}%')
    print(f'Время ожидания: Максимальное = {max(data[0])}мс, Минимальное = {min(data[0])}мс, Среднее = {round(sum(data[0])/len(data[0]),2)}мс')

if __name__ == '__main__':
    main()
