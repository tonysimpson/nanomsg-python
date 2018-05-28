import unittest
import os
import uuid
import time

from nanomsg_wrappers import set_wrapper_choice, get_default_for_platform
set_wrapper_choice(os.environ.get('NANOMSG_PY_TEST_WRAPPER',
                                  get_default_for_platform()))

from nanomsg import (
    PAIR,
    DONTWAIT,
    SOL_SOCKET,
    SNDBUF,
    poll,
    Socket,
    NanoMsgAPIError
)

SOCKET_ADDRESS = os.environ.get('NANOMSG_PY_TEST_ADDRESS', "inproc://{0}".format(uuid.uuid4()))


class TestPoll(unittest.TestCase):
    def test_read_poll(self):
        with Socket(PAIR) as s1:
            with Socket(PAIR) as s2:
                s1.bind(SOCKET_ADDRESS)
                s2.connect(SOCKET_ADDRESS)
                r, _ = poll([s1, s2], [], 0)
                self.assertEqual(0, len(r), "Precondition nothing to read")
                sent = b'ABC'
                s2.send(sent)
                r, _ = poll([s1, s2], [], 0)
                self.assertTrue(s1 in r, "Socket is in read list")
                received = s1.recv()

    def test_write_poll(self):
        with Socket(PAIR) as s1:
            with Socket(PAIR) as s2:
                s1.bind(SOCKET_ADDRESS)
                s2.connect(SOCKET_ADDRESS)
                r, w = poll([], [s1, s2], 2)
                self.assertEqual(2, len(w), "Precondition nothing to read")
                sent = b'ABCD'

                # minimum send size
                snd_buf_size = 128*1024
                s2.set_int_option(SOL_SOCKET, SNDBUF, snd_buf_size)

                # send until full
                for i in range(snd_buf_size//len(sent)+1):
                    try:
                        s2.send(sent, DONTWAIT)
                    except:
                        pass

                # poll
                r, w = poll([], [s1, s2], 0)
                self.assertTrue(s2 not in w, "Socket is in write list")
                received = s1.recv()

    def test_poll_timeout(self):
        with Socket(PAIR) as s1:
            with Socket(PAIR) as s2:
                s1.bind(SOCKET_ADDRESS)
                s2.connect(SOCKET_ADDRESS)
                start_time = time.time()
                timeout = .05
                r, _ = poll([s1, s2], [], timeout)
                end_time = time.time()
                self.assertTrue(end_time-start_time-timeout < .030)
                self.assertEqual(0, len(r), "No sockets to read")



if __name__ == '__main__':
    unittest.main()
