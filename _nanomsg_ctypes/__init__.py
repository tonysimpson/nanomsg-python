import ctypes
import platform
import sys

if 'win' in sys.platform:
    _functype = ctypes.WINFUNCTYPE
    _lib = ctypes.windll.nanomsg
else:
    _functype = ctypes.CFUNCTYPE
    _lib = ctypes.cdll.LoadLibrary('libnanomsg.so.0.0.0')


def _c_func_wrapper_factory(cdecl_text):
    def move_pointer_and_strip(type_def, name):
        if '*' in name:
            type_def += ' ' + name[:name.rindex('*')+1]
            name = name.rsplit('*', 1)[1]
        return type_def.strip(), name.strip()

    def type_lookup(type_def):
        types = {
            'void': None,
            'char *': ctypes.c_char_p,
            'int': ctypes.c_int,
            'int *': ctypes.POINTER(ctypes.c_int),
            'void *': ctypes.c_void_p,
            'size_t':  ctypes.c_size_t,
            'size_t *':  ctypes.POINTER(ctypes.c_size_t),
            'struct nn_msghdr *': ctypes.c_void_p,
        }
        type_def_without_const = type_def.replace('const ','')
        if type_def_without_const in types:
            return types[type_def_without_const]
        elif (type_def_without_const.endswith('*') and
                type_def_without_const[:-1] in types):
            return ctypes.POINTER(types[type_def_without_const[:-1]])
        else:
            raise KeyError(type_def)

        return types[type_def.replace('const ','')]

    a, b = [i.strip() for i in cdecl_text.split('(',1)]
    params, _ = b.rsplit(')',1)
    rtn_type, name = move_pointer_and_strip(*a.rsplit(' ', 1))
    param_spec = []
    for param in params.split(','):
        if param != 'void':
            param_spec.append(move_pointer_and_strip(*param.rsplit(' ', 1)))
    func = _functype(type_lookup(rtn_type),
                     *[type_lookup(type_def) for type_def, _ in param_spec])(
                        (name, _lib),
                        tuple((2 if '**' in type_def else 1, name)
                              for type_def, name in param_spec)
                    )
    func.__name__ = name
    return func


_C_HEADER = """
NN_EXPORT int nn_errno (void);
NN_EXPORT const char *nn_strerror (int errnum);
NN_EXPORT const char *nn_symbol (int i, int *value);
NN_EXPORT void nn_term (void);
NN_EXPORT void *nn_allocmsg (size_t size, int type);
NN_EXPORT int nn_freemsg (void *msg);
NN_EXPORT int nn_socket (int domain, int protocol);
NN_EXPORT int nn_close (int s);
NN_EXPORT int nn_setsockopt (int s, int level, int option, const void \
*optval, size_t optvallen);
NN_EXPORT int nn_getsockopt (int s, int level, int option, void *optval, \
size_t *optvallen);
NN_EXPORT int nn_bind (int s, const char *addr);
NN_EXPORT int nn_connect (int s, const char *addr);
NN_EXPORT int nn_shutdown (int s, int how);
NN_EXPORT int nn_send (int s, const void *buf, size_t len, int flags);
NN_EXPORT int nn_recv (int s, void *buf, size_t len, int flags);
NN_EXPORT int nn_sendmsg (int s, const struct nn_msghdr *msghdr, int flags);
NN_EXPORT int nn_recvmsg (int s, struct nn_msghdr *msghdr, int flags);
NN_EXPORT int nn_device (int s1, int s2);\
""".replace('NN_EXPORT', '')


for cdecl_text in _C_HEADER.splitlines():
    if cdecl_text.strip():
        func = _c_func_wrapper_factory(cdecl_text)
        globals()['_' + func.__name__] = func


def nn_symbols():
    "query the names and values of nanomsg symbols"
    value = ctypes.c_int()
    name_value_pairs = []
    i = 0
    while True:
        name = _nn_symbol(i, ctypes.byref(value))
        if name is None:
            break
        i += 1
        name_value_pairs.append((name, value.value))
    return name_value_pairs


nn_errno = _nn_errno
nn_errno.__doc__ = "retrieve the current errno"

nn_strerror = _nn_strerror
nn_strerror.__doc__ = "convert an error number into human-readable string"

nn_socket = _nn_socket
nn_socket.__doc__ = "create an SP socket"

nn_close = _nn_close
nn_close.__doc__ = "close an SP socket"


def nn_setsockopt(socket, level, option, value):
    """set a socket option

    socket - socket number
    level - option level
    option - option
    value - a readable byte buffer (not a Unicode string) containing the value
    returns - 0 on success or < 0 on error

    """
    buf = buffer(value)
    return _nn_setsockopt(s, level, option, buf, len(buf))


def nn_getsockopt(socket, level, option, value):
    """retrieve a socket option

    socket - socket number
    level - option level
    option - option
    value - a writable byte buffer (e.g. a bytearray) which the option value
    will be copied to
    returns - number of bytes copied or on error nunber < 0

    """
    buf = (ctypes.c_char*len(value)).from_buffer(value)
    return _nn_getsockopt(socket, level, option, buf, len(buf))


nn_bind = _nn_bind
nn_bind.__doc__ = "add a local endpoint to the socket"

nn_connect = _nn_connect
nn_connect.__doc__ = "add a remote endpoint to the socket"

nn_shutdown = _nn_shutdown
nn_shutdown.__doc__ = "remove an endpoint from a socket"


def nn_send(socket, msg, flags):
    "send a message"
    buf = buffer(msg)
    return _nn_send(s, buf, len(buf), flags)


def nn_recv(socket, msg_buf, flags):
    buf = (ctypes.c_char*len(msg_buf)).from_buffer(msg_buf)
    return _nn_recv(s, buf, len(buf))


nn_device = _nn_device
nn_device.__doc__ = "start a device"

nn_term = _nn_term
nn_term.__doc__ = "notify all sockets about process termination"


"""
    {"nn_allocmsg", _nanomsg_nn_allocmsg, METH_VARARGS, "allocate a message"}
};
"""
