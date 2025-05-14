import socket


def get_local_ip():  # Возвращает IP адрес компьютера пользователя
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    s.connect(('8.8.8.8', 80))
    return s.getsockname() [0]


def check_free_port():  # Проверяет какой порт из высоких портов свободен на компьюютере отправителя
    for port in range(49152, 65536):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return port
            except socket.error:
                continue
    return None
