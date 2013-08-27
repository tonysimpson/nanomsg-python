from pytest import *
import nanomsg


SOCKET_ADDRESS = "inproc://a"


def test_pair():

    sb = nanomsg.nn_socket(nanomsg.AF_SP, nanomsg.NN_PAIR)
    assert(sb != -1)
    rc = nanomsg.nn_bind(sb, SOCKET_ADDRESS)
    assert(rc >= 0)
    sc = nanomsg.nn_socket(nanomsg.AF_SP, nanomsg.NN_PAIR)
    assert(sc != -1)
    rc = nanomsg.nn_connect(sc, SOCKET_ADDRESS)
    assert(rc >= 0)

    rc = nanomsg.nn_send(sc, b"ABC", 0)
    assert(rc >= 0)
    assert(rc == 3)

    rc, buf = nanomsg.nn_recv(sb, 0)
    assert(rc >= 0)
    assert(rc == 3)
    assert(bytes(buf) == b"ABC")

    rc = nanomsg.nn_send(sb, b"DEF", 0)
    assert(rc >= 0)
    assert(rc == 3)

    rc, buf = nanomsg.nn_recv(sc, 0)
    assert(rc >= 0)
    assert(rc == 3)
    assert(bytes(buf) == b"DEF")

    rc = nanomsg.nn_close(sc)
    assert(rc == 0)
    rc = nanomsg.nn_close(sb)
    assert(rc == 0)
