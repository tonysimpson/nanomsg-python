#include <nanomsg/nn.h>
#include <Python.h>


static PyObject *
_nanomsg_nn_errno(PyObject *self, PyObject *args)
{
    return Py_BuildValue("i", nn_errno());
}

static PyObject *
_nanomsg_nn_strerror(PyObject *self, PyObject *args)
{
    int errno;
    if (!PyArg_ParseTuple(args, "i", &errno))
        return NULL;
    return Py_BuildValue("s", nn_strerror(errno));
}

static PyMethodDef module_methods[] = {
    {"nn_errno", _nanomsg_nn_errno, METH_VARARGS, "retrieve the current errno"},
    {"nn_strerror", _nanomsg_nn_strerror, METH_VARARGS, "convert an error number into human-readable string"},
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

