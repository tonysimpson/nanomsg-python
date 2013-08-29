import unittest
import os

from nanomsg_wrappers import set_wrapper_choice
set_wrapper_choice(os.environ.get('NANOMSG_PY_TEST_WRAPPER', "ctypes"))

from nanomsg import (
    PAIR,
    Socket
)

SOCKET_ADDRESS = os.environ.get('NANOMSG_PY_TEST_ADDRESS', "inproc://a")


class TestPairSockets(unittest.TestCase):
    def test_send_recv(self):
        with Socket(PAIR) as s1:
            with Socket(PAIR) as s2:
                s1.bind(SOCKET_ADDRESS)
                s2.connect(SOCKET_ADDRESS)

                sent = b'ABC'
                s2.send(sent)
                recieved = s1.recv()
        self.assertEqual(sent, recieved)


if __name__ == '__main__':
    unittest.main()
