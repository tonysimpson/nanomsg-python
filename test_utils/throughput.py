from __future__ import division, absolute_import, print_function,\
 unicode_literals
import os
from nanomsg_wrappers import set_wrapper_choice, get_default_for_platform
WRAPPER = os.environ.get('NANOMSG_PY_TEST_WRAPPER', get_default_for_platform())
set_wrapper_choice(WRAPPER)

from nanomsg import (
    PAIR,
    Socket,
    create_message_buffer
)

from nanomsg.wrapper import (
    nn_send,
    nn_recv
)

SOCKET_ADDRESS = os.environ.get('NANOMSG_PY_TEST_ADDRESS', "inproc://a")
import time
BUFFER_SIZE = eval(os.environ.get('NANOMSG_PY_TEST_BUFFER_SIZE', "1024"))

msg = create_message_buffer(BUFFER_SIZE, 0)

DURATION = 10

print(('Working NANOMSG_PY_TEST_BUFFER_SIZE %d NANOMSG_PY_TEST_WRAPPER %r '
       'NANOMSG_PY_TEST_ADDRESS %r') % (BUFFER_SIZE, WRAPPER, SOCKET_ADDRESS))
count = 0
start_t = time.time()
with Socket(PAIR) as socket1:
    with Socket(PAIR) as socket2:
        socket1.bind(SOCKET_ADDRESS)
        socket2.connect(SOCKET_ADDRESS)
        while time.time() < start_t + DURATION:
            c = chr(count % 255)
            memoryview(msg)[0] = c
            socket1.send(msg)
            res = socket2.recv(msg)
            assert res[0] == c
            count += 1
        stop_t = time.time()

print('Socket API throughput with checks - %f Mb/Second' % ((count * BUFFER_SIZE) / (stop_t - start_t) / 1024,))

count = 0
start_t = time.time()
with Socket(PAIR) as socket1:
    with Socket(PAIR) as socket2:
        socket1.bind(SOCKET_ADDRESS)
        socket2.connect(SOCKET_ADDRESS)
        while time.time() < start_t + DURATION:
            nn_send(socket1.fd, msg, 0)
            nn_recv(socket2.fd, msg, 0)
            count += 1
        stop_t = time.time()
print('Raw thoughtput no checks          - %f Mb/Second' % ((count * BUFFER_SIZE) / (stop_t - start_t) / 1024,))
