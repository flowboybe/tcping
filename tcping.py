#!/usr/bin/python3

import socket
import argparse

import network_utils
import sys

from ping import ping



def parse_args():  # Парсит данные с командной строки
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str,
                        help= 'IP адрес на который будет отправлен запрос (Поддерживается как домен, так и IP)')
    parser.add_argument('-p', '--port', type=int, default=80,
                        help= 'Порт для отправки запроса, по умолчанию 80')
    parser.add_argument('-t', '--timeout', type=float, default=5,
                        help= 'Время ожидания ответа в секундах, по умолчанию 5 секунд')
    parser.add_argument('-i', '--interval', type=float, default=1,
                        help= 'Интервал между запросами в секундах, по умолчанию 1 секунда')
    parser.add_argument('-n', '--count', type=int, default=float('Inf'),
                        help= 'Количество запросов, по умолчанию бесконечно')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help= 'Режим просмотра содержимого пакетов')
    args = parser.parse_args()
    return args


def check_errors(port, interval, timeout, count):
    if port < 0 or port > 65535:
        print('Выбранного порта не существует.')
        sys.exit(1)
    if interval < 0:
        print('Интервал между запросами не может быть меньше 0 секунд.')
        sys.exit(1)
    if timeout < 0:
        print('Время ожидания не может быть меньше 0 секунд.')
        sys.exit(1)
    if count < 0:
        print('Количество отправляемых запросов не может быть меньше 0.')
        sys.exit(1)


def print_statistics(outer_data):
    print(
        f'Отправлено {outer_data [1]} пакетов,'
        f' получено {outer_data [2]} пакетов,'
        f' процент потерь - {int((1 - outer_data [2] / outer_data [1]) * 100)}%')
    if len(outer_data [0]) != 0:
        print(
            f'Время ожидания: Максимальное = {max(outer_data [0])}мс,'
            f' Минимальное = {min(outer_data [0])}мс,'
            f' Среднее = {round(sum(outer_data [0]) / len(outer_data [0]), 2)}мс')


def get_info():
    args = parse_args()
    if network_utils.is_valid_ipv6(args.host): ipv = 6
    else: ipv = 4
    check_errors(args.port, args.interval, args.timeout, args.count)
    if not args.host [0].isdigit() and ipv != 6:
        try:
            dst_ip = socket.gethostbyname(args.host)
        except socket.gaierror:
            print('Указанного доменного имени не существует.')
            sys.exit(1)
    else:
        if ipv == 6:
            dst_ip = network_utils.get_local_ip(6)
        else:
            dst_ip = args.host
    if dst_ip == '127.0.0.1':
        src_ip = '127.0.0.1'
    else:
        src_ip = network_utils.get_local_ip(4)
    free_port = network_utils.check_free_port()
    return dst_ip, args.port, src_ip, free_port, args.timeout, args.interval, args.count, ipv, args.verbose


def main():
    dst_ip, dst_port, src_ip, src_port, time, interval, count, ipv, verbose = get_info()
    outer_data = [[], 0, 0]
    print(f'Начинаю отправку TCP пакетов на {dst_ip}:{dst_port} от {src_ip}:{src_port}')
    try:
        ping(src_ip, dst_ip, src_port, dst_port, time, interval, count, outer_data, ipv, verbose)
        print_statistics(outer_data)
    except KeyboardInterrupt:
        print_statistics(outer_data)


if __name__ == '__main__':
    main()
