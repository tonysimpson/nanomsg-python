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

from nanomsg import Socket, BUS, PAIR
import sys
import random
from itertools import count

with Socket(PAIR) as socket1:
    with Socket(PAIR) as socket2:
        socket1.bind(SOCKET_ADDRESS)
        socket2.connect(SOCKET_ADDRESS)
        for i in count(1):
            msg = b''.join(chr(random.randint(0,255)) for i in range(1024*1024))
            socket1.send(msg)
            res = socket2.recv()
            print i
            if msg != res:
                for num, (c1, c2) in enumerate(zip(msg, res)):
                    if c1 != c2:
                        print 'diff at', num, repr(c1), repr(c2)
                        sys.exit()





