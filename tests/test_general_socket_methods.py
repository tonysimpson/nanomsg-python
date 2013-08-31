import unittest
import os

from nanomsg_wrappers import set_wrapper_choice, get_default_for_platform
set_wrapper_choice(os.environ.get('NANOMSG_PY_TEST_WRAPPER',
                                  get_default_for_platform()))

from nanomsg import (
    PAIR,
    Socket,
    LINGER,
    SOL_SOCKET
)

SOCKET_ADDRESS = os.environ.get('NANOMSG_PY_TEST_ADDRESS', "inproc://a")

LINGER_DEFAULT_VALUE = 1000


class TestGeneralSocketMethods(unittest.TestCase):
    def setUp(self):
        self.socket = Socket(PAIR)

    def tearDown(self):
        self.socket.close()

    def test_bind(self):
        endpoint = self.socket.bind(SOCKET_ADDRESS)

        self.assertIsNotNone(endpoint)

    def test_connect(self):
        endpoint = self.socket.connect(SOCKET_ADDRESS)

        self.assertIsNotNone(endpoint)

    def test_is_open_is_true_when_open(self):
        self.assertTrue(self.socket.is_open())

    def test_is_open_is_false_when_closed(self):
        self.socket.close()

        self.assertFalse(self.socket.is_open())

    def test_set_int_option(self):
        expected = 500

        self.socket.set_int_option(SOL_SOCKET, LINGER, expected)

        actual = self.socket.get_int_option(SOL_SOCKET, LINGER)
        self.assertEqual(expected, actual)

    def test_get_int_option(self):
        actual = self.socket.get_int_option(SOL_SOCKET, LINGER)

        self.assertEqual(LINGER_DEFAULT_VALUE, actual)


if __name__ == '__main__':
    unittest.main()
