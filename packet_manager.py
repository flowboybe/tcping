import struct
import socket
import time
import random
import info


def build_syn_packet(src_ip, dst_ip, src_port, dst_port, seq, version, verbose):  # Собирает TCP пакет
    packet = struct.pack(
        '!HHIIBBHHH', # Структура полей TCP заголовка
        src_port, # Порт отправления
        dst_port, # Порт получения
        seq, # Номер последовательности
        0, # Номер подтверждения
        5 << 4, # Сдвиг данных (20 байт)
        0x02, # SYN флаг
        1024, # Размер окна
        0, # Контрольная сумма
        0 # Указатель срочности
    )

    if version == 4:
        pseudo_header = struct.pack(
            '!4s4sHH', # Структура полей псевдозаголовка
            socket.inet_aton(src_ip), #IP источника
            socket.inet_aton(dst_ip), #IP получателя
            socket.IPPROTO_TCP, # Протокол
            len(packet) # Длина TCP пакета
    )
    elif version == 6:
        pseudo_header = struct.pack(
            '!16s16sII',
            socket.inet_pton(socket.AF_INET6, src_ip),
            socket.inet_pton(socket.AF_INET6, dst_ip),
            len(packet),
            socket.IPPROTO_TCP
        )
    else:
        raise TypeError

    checksum = calculate_check_sum(pseudo_header + packet)
    packet = packet [:16] + struct.pack('H', checksum) + packet [18:] # Заменяет нулевые байты контрольной суммы

    if verbose:
        info.print_syn_info(packet)

    return packet


def send_packet(s, src_ip, dst_ip, src_port, dst_port, version, verbose):
    seq = random.randint(1, 10000000)
    tcp_packet = build_syn_packet(src_ip, dst_ip, src_port, dst_port, seq, version, verbose)
    start_time = time.time()
    if version == 4:
        s.sendto(tcp_packet, (dst_ip, dst_port))
    elif version == 6:
        s.sendto(tcp_packet, (dst_ip, 0, 0, 0))
    else:
        raise TypeError

    return seq, start_time


def receive_packet(s, src_port, dst_ip, dst_port, start_time, outer_data, seq, version, verbose):
    try:
        while True:  # Ждем получение пакета, пока не выйдет время
            response = s.recvfrom(40)
            if not response: continue
            data, _ = response

            src_port_packet, dst_port_packet, ack_num, flags = unpack_ipv_packet(data, version)

            if (src_port_packet == dst_port
            and dst_port_packet == src_port
            and ack_num == seq + 1):  # Проверка на корректность пакета
                ack_time = round((time.time() - start_time) * 1000, 2)
                if (flags & 0x14) == 0x14:  # Проверка на RST + ACK флаг
                    print(f'Порт {dst_port} закрыт.')
                elif (flags & 0x12) == 0x12:  # Проверка на ACK флаг
                    outer_data[0].append(ack_time)
                    outer_data[2] += 1
                    print(f'Получен пакет от {dst_ip}:{dst_port}, время = {ack_time}мс.')
                if verbose:
                    info.print_ack_info(data[20:40])
                break

    except socket.timeout:  # Если ответ не пришел
        print(f'Запрос на {dst_ip}:{dst_port} - Время истекло.')


def calculate_check_sum(data):  # Считает контрольную сумму для пакета
    summ = 0
    is_even = len(data) % 2

    for i in range(0, len(data) - is_even, 2):
        summ += (data[i]) + ((data[i + 1]) << 8)

    if is_even:
        summ += data[-1] << 8

    while summ >> 16:
        summ = (summ & 0xffff) + (summ >> 16)

    summ = ~summ & 0xffff

    return summ


def unpack_ipv_packet(data, version): # Распаковывает полученный пакет
    if version == 4:
        tcp_header = data [20:40] # Распаковка TCP заголовка
    else:
        tcp_header = data[40:60]
    tcph = struct.unpack('!HHLLBBHHH', tcp_header)
    src_port_packet = tcph[0]
    dst_port_packet = tcph[1]
    ack_num = tcph[3]
    flags = tcph[5]

    return src_port_packet, dst_port_packet, ack_num, flags