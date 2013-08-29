import struct
from nanomsg_wrappers import load_wrapper as _load_wrapper
import warnings

_wrapper = _load_wrapper()

#Import wrapper api into globals
globals().update(dict((k, v) for k, v in _wrapper.__dict__.iteritems()
                      if not k.startswith('_')))
for name, value in nn_symbols():
    if name.startswith('NN_'):
        name = name[3:]
    globals()[name] = value


class NanoMsgError(Exception):
    """Base Exception for all errors in the nanomsg python package

    """
    pass


class NanoMsgAPIError(NanoMsgError):
    """Exception for all errors reported by the C API.

    msg and errno are from nanomsg C library.

    """
    __slots__ = ('msg', 'errno')

    def __init__(self):
        errno = nn_errno()
        msg = nn_strerror(errno)
        NanoMsgError.__init__(self, msg)
        self.errno, self.msg = errno, msg


def _nn_check_positive_rtn(rtn):
    if rtn < 0:
        raise NanoMsgAPIError()
    return rtn


class Device(object):
    """Create a nanomsg device to relay messages between sockets.

    If only one socket is supplied the device loops messages on that socket.
    """
    def __init__(self, socket1, socket2=None):
        self._s1 = socket1._s
        self._s2 = -1 if socket2 is None else socket2._s

    def start(self):
        """Run the device in the current thread.

        This will not return until the device stops due to error or
        termination.
        """
        _nn_check_positive_rtn(nn_device(self._s1, self._s2))


def terminate_all():
    """Close all sockets and devices"""
    nn_term()


class Socket(object):
    """Class wrapping nanomsg socket.

    protocol should be a nanomsg protocol constant e.g. nanomsg.PAIR

    This class supports being used as a context manager which should gaurentee
    it is closed.

    e.g.:
        import time
        from nanomsg import PUB, Socket

        with Socket(PUB) as pub_socket:
            pub_socket.bind('tcp://127.0.0.1:49234')
            for i in range(100):
                pub_socket.send(b'hello all')
                time.sleep(0.5)
        #pub_socket is closed

    Socket.bind and Socket.connect return subclass of Endpoint which allow
    you to shutdown selected endpoints.

    """

    class Endpoint(object):
        def __init__(self, socket, endpoint_id, address):
            self._endpoint_id = endpoint_id
            self._socket = socket
            self._address = address

        @property
        def address(self):
            return self._address

        def shutdown(self):
            self._socket._endpoints.remove(self)
            _nn_check_positive_rtn(nn_shutdown(self._socket._s,
                                               self._endpoint_id))

        def __repr__(self):
            return u'<%s socket %r, id %r, addresss %r>' % (
                self.__class__.__name__,
                self._socket,
                self._endpoint_id,
                self._address
            )

    class BindEndpoint(Endpoint):
        pass

    class ConnectEndpoint(Endpoint):
        pass

    def __init__(self, protocol, domain=AF_SP):
        self._s = _nn_check_positive_rtn(nn_socket(domain, protocol))
        self._endpoints = []

    @property
    def endpoints(self):
        return list(self._endpoints)

    def bind(self, address):
        endpoint_id = _nn_check_positive_rtn(nn_bind(self._s, address))
        ep = Socket.BindEndpoint(self, endpoint_id, address)
        self._endpoints.append(ep)
        return ep

    def connect(self, address):
        endpoint_id = _nn_check_positive_rtn(nn_connect(self._s, address))
        ep = Socket.ConnectEndpoint(self, endpoint_id, address)
        self._endpoints.append(ep)
        return ep

    def close(self):
        if self.is_open():
            s = self._s
            self._s = -1
            _nn_check_positive_rtn(nn_close(s))

    def is_open(self):
        """Returns true if the socket has a valid socket id.

        If the underlying socket is closed by some other means than
        Socket.close this method may return True when the socket is actually
        closed.
        """
        return self._s >= 0

    def recv(self, buf=None, flags=0):
        if buf is None:
            rtn, out_buf = nn_recv(self._s, flags)
        else:
            rtn, out_buf = nn_recv(self._s, buf, flags)
        _nn_check_positive_rtn(rtn)
        return bytes(buffer(out_buf, 0, rtn))

    def set_string_option(self, option, value, level=SOL_SOCKET):
        _nn_check_positive_rtn(nn_setsockopt(self._s, level, option, value))

    def set_int_option(self, option, value, level=SOL_SOCKET):
        _nn_check_positive_rtn(
            nn_setsockopt(self._s, level, option, struct.pack('i', value))
        )

    def get_int_option(self, option, level=SOL_SOCKET):
        size = struct.calcsize('i')
        buf = bytearray(size)
        rtn, length = nn_getsockopt(self._s, level, option, buf)
        _nn_check_positive_rtn(rtn)
        if length != size:
            raise NanoMsgError(('Returned option size (%r) should be the same'
                                ' as size of int (%r)') % (rtn, size))
        return struct.unpack_from('i', buffer(buf))[0]

    def get_string_option(self, option, level=SOL_SOCKET, max_len=16*1024):
        buf = bytearray(max_len)
        rtn, length = nn_getsockopt(self._s, level, option, buf)
        _nn_check_positive_rtn(rtn)
        return str(buf[:length])

    def send(self, msg, flags=0):
        _nn_check_positive_rtn(nn_send(self._s, msg, flags))

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __repr__(self):
        return u'<%s id %r, connected to %r, bound to %r>' % (
            self.__class__.__name__,
            self._s,
            [i.address for i in self.endpoints if type(i) is
             Socket.BindEndpoint],
            [i.address for i in self.endpoints if type(i) is
             Socket.ConnectEndpoint],
        )

    def __del__(self):
        try:
            if self.is_open():
                warnings.warn("Maybe %r was not closed before it was GC'd" %
                              (self,))
                self.close()
        except NanoMsgError:
            pass
