from __future__ import division, absolute_import, print_function, unicode_literals

from .version import __version__
from struct import Struct as _Struct
import warnings

from . import wrapper

try:
    buffer
except NameError:
    buffer = memoryview  # py3

nanoconfig_started = False

#Import constants into module with NN_ prefix stripped
for name, value in wrapper.nn_symbols():
    if name.startswith('NN_'):
        name = name[3:]
    globals()[name] = value


if hasattr(wrapper, 'create_writable_buffer'):
    create_writable_buffer = wrapper.create_writable_buffer
else:
    def create_writable_buffer(size):
        """Returns a writable buffer"""
        return bytearray(size)


def create_message_buffer(size, type):
    """Create a message buffer"""
    rtn = wrapper.nn_allocmsg(size, type)
    if rtn is None:
        raise NanoMsgAPIError()
    return rtn


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
        errno = wrapper.nn_errno()
        msg = wrapper.nn_strerror(errno)
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
        self._fd1 = socket1.fd
        self._fd2 = -1 if socket2 is None else socket2.fd

    def start(self):
        """Run the device in the current thread.

        This will not return until the device stops due to error or
        termination.
        """
        _nn_check_positive_rtn(wrapper.nn_device(self._fd1, self._fd2))


def terminate_all():
    """Close all sockets and devices"""
    global nanoconfig_started
    if nanoconfig_started:
        wrapper.nc_term()
        nanoconfig_started = False
    wrapper.nn_term()


def poll(in_sockets, out_sockets, timeout=-1):
    """
    Poll a list of sockets
    :param in_sockets: sockets for reading
    :param out_sockets: sockets for writing
    :param timeout: poll timeout in seconds, -1 is infinite wait
    :return: tuple (read socket list, write socket list)
    """
    sockets = {}
    # reverse map fd => socket
    fd_sockets = {}
    for s in in_sockets:
        sockets[s.fd] = POLLIN
        fd_sockets[s.fd] = s
    for s in out_sockets:
        modes = sockets.get(s.fd, 0)
        sockets[s.fd] = modes | POLLOUT
        fd_sockets[s.fd] = s

    # convert to milliseconds or -1
    if timeout >= 0:
        timeout_ms = int(timeout*1000)
    else:
        timeout_ms = -1
    res, sockets = wrapper.nn_poll(sockets, timeout_ms)
    _nn_check_positive_rtn(res)
    read_list, write_list = [], []
    for fd, result in sockets.items():
        if (result & POLLIN) != 0:
            read_list.append(fd_sockets[fd])
        if (result & POLLOUT) != 0:
            write_list.append(fd_sockets[fd])

    return read_list, write_list


class Socket(object):
    """Class wrapping nanomsg socket.

    protocol should be a nanomsg protocol constant e.g. nanomsg.PAIR

    This class supports being used as a context manager which should guarantee
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

    The constructor also allows you to wrap existing sockets by passing in the
    socket fd instead of the protocol e.g.:
        from nanomsg import AF_SP, PAIR, Socket
        from nanomsg import wrapper as nn

        socket_fd = nn.nn_socket(AF_SP, PAIR)
        socket = Socket(socket_fd=socket_fd)

    """

    _INT_PACKER = _Struct(str('i'))

    class _Endpoint(object):
        def __init__(self, socket, endpoint_id, address):
            self._endpoint_id = endpoint_id
            self._fdocket = socket
            self._address = address

        @property
        def address(self):
            return self._address

        def shutdown(self):
            self._fdocket._endpoints.remove(self)
            _nn_check_positive_rtn(wrapper.nn_shutdown(self._fdocket._fd,
                                               self._endpoint_id))

        def __repr__(self):
            return '<%s socket %r, id %r, address %r>' % (
                self.__class__.__name__,
                self._fdocket,
                self._endpoint_id,
                self._address
            )

    class BindEndpoint(_Endpoint):
        pass

    class ConnectEndpoint(_Endpoint):
        pass

    class NanoconfigEndpoint(_Endpoint):

        def shutdown(self):
            raise NotImplementedError(
                "Shutdown of nanoconfig endpoint is not supported")

    def __init__(self, protocol=None, socket_fd=None, domain=AF_SP):
        if protocol is not None and socket_fd is not None:
            raise NanoMsgError('Only one of protocol or socket_fd should be '
                               'passed to the Socket constructor')
        if protocol is not None:
            self._fd = _nn_check_positive_rtn(
                wrapper.nn_socket(domain, protocol)
            )
        else:
            self._fd = socket_fd
        self._endpoints = []

    def _get_send_fd(self):
        return self.get_int_option(SOL_SOCKET, SNDFD)

    def _get_recv_fd(self):
        return self.get_int_option(SOL_SOCKET, RCVFD)

    def _get_linger(self):
        return self.get_int_option(SOL_SOCKET, LINGER)

    def _set_linger(self, value):
        return self.set_int_option(SOL_SOCKET, LINGER, value)

    def _get_send_buffer_size(self):
        return self.get_int_option(SOL_SOCKET, SNDBUF)

    def _set_send_buffer_size(self, value):
        return self.set_int_option(SOL_SOCKET, SNDBUF, value)

    def _get_recv_buffer_size(self):
        return self.get_int_option(SOL_SOCKET, RCVBUF)

    def _set_recv_buffer_size(self, value):
        return self.set_int_option(SOL_SOCKET, RCVBUF, value)

    def _get_send_timeout(self):
        return self.get_int_option(SOL_SOCKET, SNDTIMEO)

    def _set_send_timeout(self, value):
        return self.set_int_option(SOL_SOCKET, SNDTIMEO, value)

    def _get_recv_timeout(self):
        return self.get_int_option(SOL_SOCKET, RCVTIMEO)

    def _set_recv_timeout(self, value):
        return self.set_int_option(SOL_SOCKET, RCVTIMEO, value)

    def _get_reconnect_interval(self):
        return self.get_int_option(SOL_SOCKET, RECONNECT_IVL)

    def _set_reconnect_interval(self, value):
        return self.set_int_option(SOL_SOCKET, RECONNECT_IVL, value)

    def _get_reconnect_interval_max(self):
        return self.get_int_option(SOL_SOCKET, RECONNECT_IVL_MAX)

    def _set_reconnect_interval_max(self, value):
        return self.set_int_option(SOL_SOCKET, RECONNECT_IVL_MAX, value)

    send_fd = property(_get_send_fd, doc='Send file descripter')
    recv_fd = property(_get_recv_fd, doc='Receive file descripter')
    linger  = property(_get_linger, _set_linger, doc='Socket linger in '
                       'milliseconds (0.001 seconds)')
    recv_buffer_size = property(_get_recv_buffer_size, _set_recv_buffer_size,
                                doc='Receive buffer size in bytes')
    send_buffer_size = property(_get_send_buffer_size, _set_send_buffer_size,
                                doc='Send buffer size in bytes')
    send_timeout = property(_get_send_timeout, _set_send_timeout,
                            doc='Send timeout in milliseconds (0.001 seconds)')
    recv_timeout = property(_get_recv_timeout, _set_recv_timeout,
                            doc='Receive timeout in milliseconds (0.001 '
                            'seconds)')
    reconnect_interval = property(
        _get_reconnect_interval,
        _set_reconnect_interval,
        doc='Base interval between connection failure and reconnect'
        ' attempt in milliseconds (0.001 seconds).'
    )
    reconnect_interval_max = property(
        _get_reconnect_interval_max,
        _set_reconnect_interval_max,
        doc='Max reconnect interval - see C API documentation.'
    )

    @property
    def fd(self):
        """Socket file descripter.

        Note this is not an OS file descripter (see .send_fd, .recv_fd).
        """
        return self._fd

    @property
    def endpoints(self):
        """Endpoints list

        """
        return list(self._endpoints)

    @property
    def uses_nanoconfig(self):
        return (self._endpoints and
            isinstance(self._endpoints[0], Socket.NanoconfigEndpoint))

    def bind(self, address):
        """Add a local endpoint to the socket"""
        if self.uses_nanoconfig:
            raise ValueError("Nanoconfig address must be sole endpoint")
        endpoint_id = _nn_check_positive_rtn(
            wrapper.nn_bind(self._fd, address)
        )
        ep = Socket.BindEndpoint(self, endpoint_id, address)
        self._endpoints.append(ep)
        return ep

    def connect(self, address):
        """Add a remote endpoint to the socket"""
        if self.uses_nanoconfig:
            raise ValueError("Nanoconfig address must be sole endpoint")
        endpoint_id = _nn_check_positive_rtn(
            wrapper.nn_connect(self.fd, address)
        )
        ep = Socket.ConnectEndpoint(self, endpoint_id, address)
        self._endpoints.append(ep)
        return ep

    def configure(self, address):
        """Configure socket's addresses with nanoconfig"""
        global nanoconfig_started
        if len(self._endpoints):
            raise ValueError("Nanoconfig address must be sole endpoint")
        endpoint_id = _nn_check_positive_rtn(
            wrapper.nc_configure(self.fd, address)
        )
        if not nanoconfig_started:
            nanoconfig_started = True
        ep = Socket.NanoconfigEndpoint(self, endpoint_id, address)
        self._endpoints.append(ep)
        return ep

    def close(self):
        """Close the socket"""
        if self.is_open():
            fd = self._fd
            self._fd = -1
            if self.uses_nanoconfig:
                wrapper.nc_close(fd)
            else:
                _nn_check_positive_rtn(wrapper.nn_close(fd))

    def is_open(self):
        """Returns true if the socket has a valid socket id.

        If the underlying socket is closed by some other means than
        Socket.close this method may return True when the socket is actually
        closed.
        """
        return self.fd >= 0

    def recv(self, buf=None, flags=0):
        """Recieve a message."""
        if buf is None:
            rtn, out_buf = wrapper.nn_recv(self.fd, flags)
        else:
            rtn, out_buf = wrapper.nn_recv(self.fd, buf, flags)
        _nn_check_positive_rtn(rtn)
        return bytes(buffer(out_buf))[:rtn]

    def set_string_option(self, level, option, value):
        _nn_check_positive_rtn(wrapper.nn_setsockopt(self.fd, level, option,
                               value))

    def set_int_option(self, level, option, value):
        buf = create_writable_buffer(Socket._INT_PACKER.size)
        Socket._INT_PACKER.pack_into(buf, 0, value)
        _nn_check_positive_rtn(wrapper.nn_setsockopt(self.fd, level, option,
                                                     buf))

    def get_int_option(self, level, option):
        size = Socket._INT_PACKER.size
        buf = create_writable_buffer(size)
        rtn, length = wrapper.nn_getsockopt(self._fd, level, option, buf)
        _nn_check_positive_rtn(rtn)
        if length != size:
            raise NanoMsgError(('Returned option size (%r) should be the same'
                                ' as size of int (%r)') % (length, size))
        return Socket._INT_PACKER.unpack_from(buffer(buf))[0]

    def get_string_option(self, level, option, max_len=16*1024):
        buf = create_writable_buffer(max_len)
        rtn, length = wrapper.nn_getsockopt(self._fd, level, option, buf)
        _nn_check_positive_rtn(rtn)
        return bytes(buffer(buf))[:length]

    def send(self, msg, flags=0):
        """Send a message"""
        _nn_check_positive_rtn(wrapper.nn_send(self.fd, msg, flags))

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __repr__(self):
        return '<%s fd %r, connected to %r, bound to %r>' % (
            self.__class__.__name__,
            self.fd,
            [i.address for i in self.endpoints if type(i) is
             Socket.ConnectEndpoint],
            [i.address for i in self.endpoints if type(i) is
             Socket.BindEndpoint],
        )

    def __del__(self):
        try:
            self.close()
        except NanoMsgError:
            pass
