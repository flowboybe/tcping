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

print(get_local_ip(6))