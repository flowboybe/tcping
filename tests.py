import socket
import struct
import unittest
from unittest.mock import patch

from packet_manager import build_syn_packet, unpack_ipv_packet, calculate_check_sum
from ping import ping


class Tests(unittest.TestCase):

    def test_ping_timeout(self): # Проверка на установку таймаута получения ответа
        with patch('socket.socket') as mock_socket:
            mock_socket.return_value.recvfrom.side_effect = socket.timeout()
            data = [[], 0, 0]
            with patch('builtins.print') as mock_print:
                ping('127.0.0.1', '127.0.0.1', 12345, 80,
                     0.5, 1, 1, data, 4, False)
                mock_socket.return_value.settimeout.assert_called_with(0.5)
                mock_print.assert_called_with('Запрос на 127.0.0.1:80 - Время истекло.')
                self.assertTrue(mock_socket.return_value.sendto.called)


    def test_ping_count(self): # Проверка на установку количества запросов
        with patch('socket.socket') as mock_socket:
            mock_socket.return_value.recvfrom.side_effect = socket.timeout()
            data = [[], 0, 0]
            with patch('builtins.print') as mock_print:
                ping('127.0.0.1', '127.0.0.1', 12345, 80,
                     1, 1, 2, data, 4, False)
                self.assertEqual(mock_print.call_count, 2)
                self.assertTrue(mock_socket.return_value.sendto.called)


    def test_ping_interval(self): # Проверка на установку интервала между отправкой запросов
        with patch('socket.socket') as mock_socket:
            mock_socket.return_value.recvfrom.side_effect = socket.timeout()
            data = [[], 0, 0]
            with patch('time.sleep') as mock_sleep:
                ping('127.0.0.1', '127.0.0.1', 12345, 80,
                     1, 2, 2, data, 4, False)
                mock_sleep.assert_called_with(2)
                self.assertTrue(mock_socket.return_value.sendto.called)


    def test_open_port(self): # Проверка на открытый  порт
        ip_header = bytes(20)
        tcp_header = struct.pack(
            '!HHIIBBHHH',
            53,
            54321,
            12345,
            2,
            5 << 4,
            0x12,
            5840,
            0,
            0
        )
        fake_response = ip_header + tcp_header
        data = [[], 0, 0]
        with patch('socket.socket') as mock_socket:
            with patch('builtins.print') as mock_print:
                with patch('packet_manager.random') as mock_random:
                    mock_random.randint.return_value = 1
                    mock_socket.return_value.recvfrom.return_value = (fake_response, ('8.8.8.8', 53))
                    ping('127.0.0.1', '8.8.8.8', 54321, 53,
                         5, 1, 1, data, 4, False)
                    self.assertEqual(mock_socket.return_value.sendto.call_count, 1)
                    args, _ = mock_print.call_args
                    self.assertTrue(args[0].startswith('Получен пакет от 8.8.8.8:53, время = '))


    def test_closed_port(self): # Проверка на закрытый порт
        ip_header = bytes(20)
        tcp_header = struct.pack(
            '!HHIIBBHHH',
            53,
            54321,
            12345,
            2,
            5 << 4,
            0x14,
            5840,
            0,
            0
        )
        fake_response = ip_header + tcp_header
        data = [[], 0, 0]
        with patch('socket.socket') as mock_socket:
            with patch('builtins.print') as mock_print:
                with patch('packet_manager.random') as mock_random:
                    mock_random.randint.return_value = 1
                    mock_socket.return_value.recvfrom.return_value = (fake_response, ('8.8.8.8', 53))
                    ping('127.0.0.1', '8.8.8.8', 54321, 53,
                         5, 1, 1, data, 4, False)
                    self.assertEqual(mock_socket.return_value.sendto.call_count, 1)
                    mock_print.assert_called_with('Порт 53 закрыт.')


    def test_timeout_port(self): # Проверка на неотвечающий порт
        data = [[], 0, 0]
        with patch('socket.socket') as mock_socket:
            with patch('builtins.print') as mock_print:
                mock_socket.return_value.recvfrom.side_effect = socket.timeout()
                ping('127.0.0.1', '8.8.8.8', 54321, 53, 5, 1, 1, data, 4, False)
                mock_print.assert_called_with('Запрос на 8.8.8.8:53 - Время истекло.')


    def test_building_syn_packet(self): # Проверка на корректность сборки SYN-пакета
        testing_packet = build_syn_packet('127.0.0.1', '8.8.8.8', 49152, 80, 1, 4, False)
        self.assertEqual(testing_packet, b'\xc0\x00\x00P\x00\x00\x00\x01\x00\x00\x00\x00P\x02\x04\x00\\\x80\x00\x00')


    def test_ipv_unpacking(self): # Проверка на корректность распаковки пакета
        testing_packet = \
            b'E\x00\x00,\x00\x00@\x00x\x06\x87\x00\xd1U\xe9d\xc0\xa8\x00i\x00P\xc0\x00\x1b\xa8\x14?\x001\xcc\xab`\x12\xff\xff_\x86\x00\x00'
        data = unpack_ipv_packet(testing_packet, 4)
        self.assertEqual(data, (80, 49152, 3263659, 18))


    def test_checksum(self): # Проверка на корректность вычисления контрольной суммы
        packet = struct.pack(
            '!HHIIBBHHH',
            49152,
            53,
            42,
            0,
            5 << 4,
            0x02,
            1024,
            0,
            0
        )
        pseudo_header = struct.pack(
            '!4s4sHH',
            socket.inet_aton('188.80.82.132'),
            socket.inet_aton('8.8.8.8'),
            socket.IPPROTO_TCP,
            len(packet)
        )
        self.assertEqual(calculate_check_sum(pseudo_header + packet), 40652)


if __name__ == '__main__':
    unittest.main()