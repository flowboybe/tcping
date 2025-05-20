import socket
import unittest
from unittest.mock import patch

from ping import ping


class Tests(unittest.TestCase):

    def test_ping_timeout(self):
        with patch('socket.socket') as mock_socket:
            mock_socket.return_value.recvfrom.side_effect = socket.timeout()
            data = [[], 0, 0]
            with patch('builtins.print') as mock_print:
                ping('127.0.0.1', '127.0.0.1', 12345, 80,
                     0.5, 1, 1, data, 4, False)
                mock_socket.return_value.settimeout.assert_called_with(0.5)
                mock_print.assert_called_with('Запрос на 127.0.0.1:80 - Время истекло')
                self.assertTrue(mock_socket.return_value.sendto.called)


    def test_ping_count(self):
        with patch('socket.socket') as mock_socket:
            mock_socket.return_value.recvfrom.side_effect = socket.timeout()
            data = [[], 0, 0]
            with patch('builtins.print') as mock_print:
                ping('127.0.0.1', '127.0.0.1', 12345, 80,
                     1, 1, 2, data, 4, False)
                self.assertEqual(mock_print.call_count, 2)
                self.assertTrue(mock_socket.return_value.sendto.called)


    def test_ping_interval(self):
        with patch('socket.socket') as mock_socket:
            mock_socket.return_value.recvfrom.side_effect = socket.timeout()
            data = [[], 0, 0]
            with patch('time.sleep') as mock_sleep:
                ping('127.0.0.1', '127.0.0.1', 12345, 80,
                     1, 2, 2, data, 4, False)
                mock_sleep.assert_called_with(2)
                self.assertTrue(mock_socket.return_value.sendto.called)


if __name__ == '__main__':
    unittest.main()