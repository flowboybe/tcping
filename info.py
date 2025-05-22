import struct

def print_info(packet, flag_type): # Подробная информация о пакете
    (src_port, dst_port, seq_num, ack_num,
     offset_reserved_flags, flags, window_size,
     checksum, urg_ptr) = struct.unpack('!HHIIBBHHH', packet[:20])

    if flag_type == 'SYN':
        flags_field = ((offset_reserved_flags << 8) | flags)
        data_offset = offset_reserved_flags >> 4
    elif flag_type == 'ACK':
        flags_field = offset_reserved_flags & 0x1FF
        data_offset = (offset_reserved_flags >> 12) & 0xF

    print(f"\n[Информация об отправленном пакете {flag_type}]")
    print("┌──────────────────────────┬──────────────────────┐")
    print(f"│ {'Исходящий порт':<24} │ {src_port:>20} │")
    print(f"│ {'Порт назначения':<24} │ {dst_port:>20} │")
    print("├──────────────────────────┼──────────────────────┤")
    print(f"│ {'Номер последовательности':<24} │ {seq_num:>20} │")
    print(f"│ {'Номер подтверждения':<24} │ {ack_num:>20} │")
    print("├──────────────────────────┼──────────────────────┤")
    print(f"│ {'Смещение данных':<24} │ {data_offset:>20} │")
    print(f"│ {'Флаги':<24} │ {bin(flags_field):>20} │")
    print(f"│ {'Размер окна':<24} │ {window_size:>20} │")
    print(f"│ {'Контрольная сумма':<24} │ {hex(checksum):>20} │")
    print(f"│ {'Указатель срочности':<24} │ {urg_ptr:>20} │")
    print("└──────────────────────────┴──────────────────────┘")

    print("\nHEX-дамп пакета:")
    hex_str = ' '.join(f"{b:02x}" for b in packet[:40])
    print(hex_str)
