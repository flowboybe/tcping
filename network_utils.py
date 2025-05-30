import socket
import sys


def get_ping_addr(host, v6): # Возвращает адрес на который будет отправлен запрос
    if v6:
        if is_valid_ipv6(host): return host
        else:
            ipv6s = get_ipv6_address(host)
            if len(ipv6s) > 0:
                return ipv6s[0]
            else:
                print('Не найдено ни одного IPv6 адреса для этого хоста.')
                sys.exit(1)
    else:
        if not host[0].isdigit():
            try:
                dst_ip = socket.gethostbyname(host)
            except socket.gaierror:
                print('Не найдено ни одного IPv4 адреса для этого хоста.')
                sys.exit(1)
        else:
            dst_ip = host
        return dst_ip


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


def get_ipv6_address(hostname):
    try:
        addr_info = socket.getaddrinfo(hostname, None, socket.AF_INET6)
        ipv6_addresses = [info[4][0] for info in addr_info]
        return ipv6_addresses
    except socket.gaierror:
        print('Данный компьютер не имеет IPv6 адреса.')
        sys.exit(1)


def check_free_port():  # Проверяет какой порт из высоких портов свободен на компьюютере отправителя
    for port in range(49152, 65536):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return port
            except socket.error:
                continue
    return None
