nanomsg-python
==============

Barebones wrapper for [nanomsg](http://nanomsg.org/).

Like nanomsg this library is still alpha.

The future plan includes a higher level API with good things like context
managers, namespaces and exceptions.

Support is planned for python 2.6, 2.7 and 3.2+ and eventually Pypy.

Bugs and change requests can be made
[here](https://github.com/tonysimpson/nanomsg-python/issues).

Py3 Example
===========

*Note: this code skips error checking for clarity, in reality you should do error checking in the same way as you would in the C API. At some time there will be a higher level API which does this for you by raising exceptions.*

    import nanomsg
    s1 = nanomsg.nn_socket(nanomsg.AF_SP, nanomsg.NN_PAIR)
    s2 = nanomsg.nn_socket(nanomsg.AF_SP, nanomsg.NN_PAIR)
    nanomsg.nn_bind(s1, 'inproc://bob')
    nanomsg.nn_connect(s2, 'inproc://bob')
    nanomsg.nn_send(s1, b'hello nanomsg', 0)
    result, buffer = nanomsg.nn_recv(s2, 0)
    print(bytes(buffer)) # in Py2 use str instead of bytes
    nanomsg.nn_term()


API
===

The API is based on the C API for nanomsg and only differes where necessary.

See the C API for further reference
[C API](http://nanomsg.org/v0.1/nanomsg.7.html).

The library makes use of the python buffer protocol to allow zero-copy operation.


Differences from C API
----------------------

**_nanomsg.Message type**

wraps msg buffers created by nanomsg, it supports the buffer protocol and
conversion to a byte string (str function in py2 and bytes function in py3).


**nn_allocmsg**

returns a _nanomsg.Message or None on error


**nn_recv**

returns a 2 tuple of (result, buffer), if can be called with a buffer e.g.

    > recv_buf = bytearray(5)
    > nanomsg.nn_recv(s1, recv_buf, 0)
    (13, bytearray(b'hello nanomsg'))

*Note: the buffer is always returned.*

Or without one and nanomsg will allocate one for you e.g.

    >nanomsg.nn_recv(s1, 0)
    (13, <_nanomsg.Message size 13, address 0x2559e70 >)

*Note: the buffer will be None on error.*

The advantage of this is you don't need to know how big the recv buffer needs to
be.


**nn_send**

Gets length from the buffer e.g.

    > nanomsg.nn_send(s2, b'hello nanomsg', 0)
    13


Not implmented yet
------------------
* nn_recvmsg
* nn_sendmsg
* nn_symbol
* nn_cmsg
* nn_freemsg -- is done automatically for you when _nanomsg.Message is GC'd this may change


Licence
=======

MIT


Authors
=======

[Tony Simpson](github.com/tonysimpson)
