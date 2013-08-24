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

    rc = nanomsg.nn_send_string(sc, "ABC", 0)
    assert(rc >= 0)
    assert(rc == 3)

    rc, buf = nanomsg.nn_recv_string(sb, 0)
    assert(rc >= 0)
    assert(rc == 3)
    assert(buf == "ABC")

    rc = nanomsg.nn_send_string(sb, "DEF", 0)
    assert(rc >= 0)
    assert(rc == 3)

    rc, buf = nanomsg.nn_recv_string(sc, 0)
    assert(rc >= 0)
    assert(rc == 3)
    assert(buf == "DEF")

    rc = nanomsg.nn_close(sc)
    assert(rc == 0)
    rc = nanomsg.nn_close(sb)
    assert(rc == 0)
