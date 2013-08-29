from pytest import *

from nanomsg import (
    PAIR,
    Socket
)

SOCKET_ADDRESS = "inproc://a"

def test_pair():
    with Socket(PAIR) as s1:
        with Socket(PAIR) as s2:
            s1.bind(SOCKET_ADDRESS)
            s2.connect(SOCKET_ADDRESS)

            sent = b'ABC'
            s2.send(sent)
            recieved = s1.recv()

            assert sent == recieved


