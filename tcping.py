#!/usr/bin/python3

import socket
import argparse
import network_utils
import sys

from ping import ping


def parse_args():  # Парсит данные с командной строки
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str,
                        help='IP адрес на который будет отправлен запрос (Поддерживается как домен, так и IP)')
    parser.add_argument('-p', '--port', type=float, default=80, help='Порт для отправки запроса, по умолчанию 80')
    parser.add_argument('-t', '--timeout', type=float, default=5,
                        help='Время ожидания ответа в секундах, по умолчанию 5 секунд')
    parser.add_argument('-i', '--interval', type=float, default=1,
                        help='Интервал между запросами в секундах, по умолчанию 1 секунда')
    parser.add_argument('-n', '--count', type=int, default=float('Inf'),
                        help='Количество запросов, по умолчанию бесконечно')
    args = parser.parse_args()
    return args


def check_errors(port, interval, timeout, count):
    if port < 0 or port > 65535:
        print('Выбранного порта не существует.')
        sys.exit()
    if interval < 0:
        print('Интервал между запросами не может быть меньше 0 секунд.')
        sys.exit()
    if timeout < 0:
        print('Время ожидания не может быть меньше 0 секунд.')
        sys.exit()
    if count < 0:
        print('Количество отправляемых запросов не может быть меньше 0.')
        sys.exit()


def print_statistics(outer_data):
    print(
        f'Отправлено {outer_data [1]} пакетов, получено {outer_data [2]} пакетов, процент потерь - {int((1 - outer_data [2] / outer_data [1]) * 100)}%')
    if len(outer_data [0]) != 0:
        print(
            f'Время ожидания: Максимальное = {max(outer_data [0])}мс, Минимальное = {min(outer_data [0])}мс, Среднее = {round(sum(outer_data [0]) / len(outer_data [0]), 2)}мс')


def main():
    args = parse_args()
    check_errors(args.port, args.interval, args.timeout, args.count)
    if not args.host [0].isdigit():
        try:
            dst_ip = socket.gethostbyname(args.host)
        except socket.gaierror:
            print('Указанного доменного имени не существует.')
            sys.exit()
    else:
        dst_ip = args.host
    src_ip = network_utils.get_ip()
    free_port = network_utils.check_free_port()
    outer_data = [[], 0, 0]
    print(f'Начинаю отправку TCP пакетов на {dst_ip}:{args.port} от {src_ip}:{free_port}')
    try:
        ping(src_ip, dst_ip, free_port, args.port, args.timeout, args.interval, args.count, outer_data)
        print_statistics(outer_data)
    except KeyboardInterrupt:
        print_statistics(outer_data)


if __name__ == '__main__':
    main()
