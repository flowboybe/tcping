import socket


def get_local_ip(version):  # Возвращает IP адрес компьютера пользователя
    if version == 4:
        ip_prot = socket.AF_INET
        dns_ip = '8.8.8.8'
    elif version == 6:
        ip_prot = socket.AF_INET6
        dns_ip = '2001:4860:4860::8888'
    else:
        raise TypeError
    s = socket.socket(ip_prot, socket.SOCK_DGRAM)  # UDP
    s.connect((dns_ip, 80))
    return s.getsockname()[0]

def is_valid_ipv6(ip): # Проверяет IPv6 на валидность
    try:
        socket.inet_pton(socket.AF_INET6, ip)
        return True
    except socket.error:
        return False


def check_free_port():  # Проверяет какой порт из высоких портов свободен на компьюютере отправителя
    for port in range(49152, 65536):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return port
            except socket.error:
                continue
    return None
