#include <nanomsg/nn.h>
#include <Python.h>

// This might be a good idea or not
#ifndef NO_CONCURRENY
#define CONCURRENCY_POINT_BEGIN Py_BEGIN_ALLOW_THREADS
#define CONCURRENCY_POINT_END Py_END_ALLOW_THREADS
#else
#define CONCURRENCY_POINT_BEGIN
#define CONCURRENCY_POINT_END
#endif

static PyObject *
_nanomsg_nn_errno(PyObject *self, PyObject *args)
{
    return Py_BuildValue("i", nn_errno());
}

static PyObject *
_nanomsg_nn_strerror(PyObject *self, PyObject *args)
{
    int error_number;
    if (!PyArg_ParseTuple(args, "i", &error_number))
        return NULL;
    return Py_BuildValue("s", nn_strerror(error_number));
}

static PyObject *
_nanomsg_nn_socket(PyObject *self, PyObject *args)
{
    int domain, protocol;
    if (!PyArg_ParseTuple(args, "ii", &domain, &protocol))
        return NULL;
    return Py_BuildValue("i", nn_socket(domain, protocol));
}

static PyObject *
_nanomsg_nn_close(PyObject *self, PyObject *args)
{
    int nn_result;
    int socket;
    if (!PyArg_ParseTuple(args, "i", &socket))
        return NULL;
    CONCURRENCY_POINT_BEGIN
    nn_result = nn_close(socket);
    CONCURRENCY_POINT_END
    return Py_BuildValue("i", nn_result);
}

static PyObject *
_nanomsg_nn_setsockopt_int(PyObject *self, PyObject *args)
{
    int socket, level, option, value;
    if (!PyArg_ParseTuple(args, "iiii", &socket, &level, &option, &value))
        return NULL;
    return Py_BuildValue("i", nn_setsockopt(socket, level, option, &value, sizeof(value)));
}

static PyObject *
_nanomsg_nn_setsockopt_string(PyObject *self, PyObject *args)
{
    int socket, level, option;
    int nn_result;
    Py_buffer value;
    if (!PyArg_ParseTuple(args, "iiis*", &socket, &level, &option, &value))
        return NULL;
    nn_result = nn_setsockopt(socket, level, option, value.buf, value.len);
    PyBuffer_Release(&value);
    return Py_BuildValue("i", nn_result);
}

static PyObject *
_nanomsg_nn_getsockopt_int(PyObject *self, PyObject *args)
{
    int socket, level, option, value;
    size_t size;
    int nn_result;
    if (!PyArg_ParseTuple(args, "iii", &socket, &level, &option))
        return NULL;
    size = 4;
    nn_result = nn_getsockopt(socket, level, option, &value, &size);
    return Py_BuildValue("ii", nn_result, value);
}

static PyObject *
_nanomsg_nn_getsockopt_string(PyObject *self, PyObject *args)
{
    int socket, level, option;
    size_t size;
    int nn_result;
    void* buffer;
    PyObject* py_obj;
    if (!PyArg_ParseTuple(args, "iiii", &socket, &level, &option, &size))
        return NULL;
    buffer = malloc(size);
    nn_result = nn_getsockopt(socket, level, option, buffer, &size);
    py_obj = Py_BuildValue("is#", nn_result, buffer, size);
    free(buffer);
    return py_obj;
}

static PyObject *
_nanomsg_nn_bind(PyObject *self, PyObject *args)
{
    int socket;
    const char *address;
    if (!PyArg_ParseTuple(args, "is", &socket, &address))
        return NULL;
    return Py_BuildValue("i", nn_bind(socket, address));
}

static PyObject *
_nanomsg_nn_connect(PyObject *self, PyObject *args)
{
    int socket;
    const char *address;
    if (!PyArg_ParseTuple(args, "is", &socket, &address))
        return NULL;
    return Py_BuildValue("i", nn_connect(socket, address));
}

static PyObject *
_nanomsg_nn_shutdown(PyObject *self, PyObject *args)
{
    int nn_result;
    int domain, protocol;
    if (!PyArg_ParseTuple(args, "ii", &domain, &protocol))
        return NULL;

    CONCURRENCY_POINT_BEGIN
    nn_result = nn_socket(domain, protocol);
    CONCURRENCY_POINT_END
    return Py_BuildValue("i", nn_result);
}

static PyObject *
_nanomsg_nn_send_string(PyObject *self, PyObject *args)
{
    int nn_result;
    int socket, length, flags;
    const char *buffer;
    if (!PyArg_ParseTuple(args, "is#i", &socket, &buffer, &length, &flags))
        return NULL;
    CONCURRENCY_POINT_BEGIN
    nn_result = nn_send(socket, buffer, length, flags);
    CONCURRENCY_POINT_END
    return Py_BuildValue("i", nn_result);
}

static PyObject *
_nanomsg_nn_recv_string(PyObject *self, PyObject *args)
{
    int nn_result;
    int socket, flags, length;
    char *buffer;
    PyObject *py_object;
    if (!PyArg_ParseTuple(args, "ii", &socket, &flags))
        return NULL;
    CONCURRENCY_POINT_BEGIN
    nn_result = nn_recv(socket, &buffer, NN_MSG, flags);
    CONCURRENCY_POINT_END
    length = nn_result < 0 ? 0 : nn_result;
    py_object = Py_BuildValue("is#", nn_result, buffer, length);
    if (nn_result < 0) {
        nn_freemsg(buffer);
    }
    return py_object;
}

static PyObject *
_nanomsg_nn_device(PyObject *self, PyObject *args)
{
    int socket_1, socket_2;
    if (!PyArg_ParseTuple(args, "ii", &socket_1, &socket_2))
        return NULL;
    return Py_BuildValue("i", nn_device(socket_1, socket_2));
}

static PyObject *
_nanomsg_nn_term(PyObject *self, PyObject *args)
{
    nn_term();
    Py_RETURN_NONE;
}

static PyMethodDef module_methods[] = {
    {"nn_errno", _nanomsg_nn_errno, METH_VARARGS, "retrieve the current errno"},
    {"nn_strerror", _nanomsg_nn_strerror, METH_VARARGS, "convert an error number into human-readable string"},
    {"nn_socket", _nanomsg_nn_socket, METH_VARARGS, "create an SP socket"},
    {"nn_close", _nanomsg_nn_close, METH_VARARGS, "close an SP socket"},
    {"nn_setsockopt_int", _nanomsg_nn_setsockopt_int, METH_VARARGS, "set a socket option - int variant"},
    {"nn_setsockopt_string", _nanomsg_nn_setsockopt_string, METH_VARARGS, "set a socket option - string or buffer variant"},
    {"nn_getsockopt_int", _nanomsg_nn_getsockopt_int, METH_VARARGS, "retrieve a socket option - int variant"},
    {"nn_getsockopt_string", _nanomsg_nn_getsockopt_string, METH_VARARGS, "retrieve a socket option - string variant"},
    {"nn_bind", _nanomsg_nn_bind, METH_VARARGS, "add a local endpoint to the socket"},
    {"nn_connect", _nanomsg_nn_connect, METH_VARARGS, "add a remote endpoint to the socket"},
    {"nn_shutdown", _nanomsg_nn_shutdown, METH_VARARGS, "remove an endpoint from a socket"},
    {"nn_send_string", _nanomsg_nn_send_string, METH_VARARGS, "send a message - string variant"},
    {"nn_recv_string", _nanomsg_nn_recv_string, METH_VARARGS, "receive a message - string variant"},
    {"nn_device", _nanomsg_nn_device, METH_VARARGS, "start a device"},
    {"nn_term", _nanomsg_nn_term, METH_VARARGS, "notify all sockets about process termination"},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
init_nanomsg(void)
{
    PyObject *m;

    m = Py_InitModule("_nanomsg", module_methods);
    if (m == NULL)
        return;
}

