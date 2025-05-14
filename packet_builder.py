import struct
import socket


def build_packet(src_ip, dst_ip, src_port, dst_port, seq, flags):  # Собирает TCP пакет
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


def calculate_check_sum(msg):  # Считает контрольную сумму для пакета
    sum_ = 0
    is_even = len(msg) % 2
    for i in range(0, len(msg) - is_even, 2):
        sum_ += (msg [i]) + ((msg [i + 1]) << 8)
    if len(msg) % 2 != 0:
        sum_ += msg [-1] << 8
    while sum_ >> 16:
        sum_ = (sum_ & 0xFFFF) + (sum_ >> 16)
    sum_ = ~sum_ & 0xffff
    return sum_
