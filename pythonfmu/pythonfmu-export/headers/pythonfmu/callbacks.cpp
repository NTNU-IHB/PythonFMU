#include <Python.h>
#include <stdio.h>

#include "cppfmu/cppfmu_common.hpp"

extern "C" {
    static const fmi2CallbackFunctions *embedded_logger;

    static PyObject*
    fmi2facade_log(PyObject *self, PyObject *args)
    {
        printf("in c code");
        if(!PyArg_ParseTuple(args, ":log"))
            return NULL;
        printf("before logger call");
        embedded_logger->logger(NULL, instance_name, fmi2OK, "ok", "test log message");
        
        Py_RETURN_NONE;
    }

    static PyObject*
    fmi2facade_test(PyObject *self, PyObject *args)
    {
        const char *msg;
        if(!PyArg_ParseTuple(args, "s:test", &msg))
            return NULL;
        printf("%s\n", msg);
        
        Py_RETURN_NONE;
    }

    static PyMethodDef EmbMethods[] = {
        {"log", fmi2facade_log, METH_VARARGS,
        "Return the number of arguments received by the process."},
        {"test", fmi2facade_test, METH_VARARGS,
        "Test Python callback function."},
        {NULL, NULL, 0, NULL}
    };

    static PyModuleDef EmbModule = {
        PyModuleDef_HEAD_INIT, "fmi2facade", NULL, -1, EmbMethods,
        NULL, NULL, NULL, NULL
    };

    static PyObject*
    PyInit_emb(void)
    {
        return PyModule_Create(&EmbModule);
    }
}