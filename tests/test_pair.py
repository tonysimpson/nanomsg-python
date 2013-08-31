import unittest
import os

from nanomsg_wrappers import set_wrapper_choice, get_default_for_platform
set_wrapper_choice(os.environ.get('NANOMSG_PY_TEST_WRAPPER',
                                  get_default_for_platform()))

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

    def test_send_recv_with_embeded_nulls(self):
        with Socket(PAIR) as s1:
            with Socket(PAIR) as s2:
                s1.bind(SOCKET_ADDRESS)
                s2.connect(SOCKET_ADDRESS)

                sent = b'ABC\x00DEFEDDSS'
                s2.send(sent)
                recieved = s1.recv()
        self.assertEqual(sent, recieved)

    def test_send_recv_large_message(self):
        with Socket(PAIR) as s1:
            with Socket(PAIR) as s2:
                s1.bind(SOCKET_ADDRESS)
                s2.connect(SOCKET_ADDRESS)

                sent = b'B'*(1024*1024)
                s2.send(sent)
                recieved = s1.recv()
        self.assertEqual(sent, recieved)




if __name__ == '__main__':
    unittest.main()
