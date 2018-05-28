nanomsg-python
==============

Python library for [nanomsg](http://nanomsg.org/) which does not compromise on
usability or performance.

Like nanomsg this library is still experimental, the API is fairly stable but
if you plan to use it at this time be prepared to get your hands dirty,
fixes and enhancements are very welcome.

The following versions of Python are supported CPython 2.6+, 3.2+ and Pypy 2.1.0+

Bugs and change requests can be made
[here](https://github.com/tonysimpson/nanomsg-python/issues).


nanommsg library in /usr/local
==============================


If you're nanomsg is in /usr/local and your machine is not configured to find it there you can rename the usr_local_setup.cfg to setup.cfg to fix the problem.


Example
=======

```python
from __future__ import print_function
from nanomsg import Socket, PAIR, PUB
s1 = Socket(PAIR)
s2 = Socket(PAIR)
s1.bind('inproc://bob')
s2.connect('inproc://bob')
s1.send(b'hello nanomsg')
print(s2.recv())
s1.close()
s2.close()
```

Or if you don't mind nesting you can use Socket as a context manager

```python
with Socket(PUB) as pub_socket:
    .... do something with pub_socket
# socket is closed
```

The lower level API is also available if you need the additional control or
performance, but it is harder to use. Error checking left out for brevity.

```python
from nanomsg import wrapper as nn_wrapper
from nanomsg import PAIR, AF_SP

s1 = nn_wrapper.nn_socket(AF_SP, PAIR)
s2 = nn_wrapper.nn_socket(AF_SP, PAIR)
nn_wrapper.nn_bind(s1, 'inproc://bob')
nn_wrapper.nn_connect(s2, 'inproc://bob')
nn_wrapper.nn_send(s1, b'hello nanomsg', 0)
result, buffer = nn_wrapper.nn_recv(s2, 0)
print(bytes(buffer))
nn_wrapper.nn_term()
```

License
=======

MIT


Authors
=======

[Tony Simpson](https://github.com/tonysimpson)
