import unittest
import os

from nanomsg_wrappers import set_wrapper_choice, get_default_for_platform
set_wrapper_choice(os.environ.get('NANOMSG_PY_TEST_WRAPPER',
                                  get_default_for_platform()))

from nanomsg import (
    SUB,
    PUB,
    SUB_SUBSCRIBE,
    Socket
)

SOCKET_ADDRESS = os.environ.get('NANOMSG_PY_TEST_ADDRESS', "inproc://a")


class TestPubSubSockets(unittest.TestCase):
    def test_subscribe_works(self):
        with Socket(PUB) as s1:
            with Socket(SUB) as s2:
                s1.bind(SOCKET_ADDRESS)
                s2.connect(SOCKET_ADDRESS)
                s2.set_string_option(SUB, SUB_SUBSCRIBE, 'test')
                s1.send('test')
                s2.recv()
                s1.send('a') # should not get received
                expected = b'test121212'
                s1.send(expected)

                actual = s2.recv()

                self.assertEquals(expected, actual)

if __name__ == '__main__':
    unittest.main()
