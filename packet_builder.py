import struct
import socket


def build_syn_packet(src_ip, dst_ip, src_port, dst_port, seq):  # Собирает TCP пакет
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

    pseudo_header = struct.pack(
        '!4s4sHH', #Структура полей псевдозаголовка
        socket.inet_aton(src_ip), #IP источника
        socket.inet_aton(dst_ip), #IP получателя
        socket.IPPROTO_TCP, # Протокол
        len(packet) # Длина TCP пакета
    )

    checksum = calculate_check_sum(pseudo_header + packet)
    packet = packet [:16] + struct.pack('H', checksum) + packet [18:] # Заменяет нулевые байты контрольной суммы

    return packet


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
