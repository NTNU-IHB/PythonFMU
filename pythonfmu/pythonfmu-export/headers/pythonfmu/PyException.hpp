
#ifndef PYTHONFMU_EXPORT_PYEXCEPTION_HPP
#define PYTHONFMU_EXPORT_PYEXCEPTION_HPP

#include "cppfmu/cppfmu_common.hpp"

#include <Python.h>
#include <iostream>
#include <sstream>

namespace pythonfmu
{

inline void handle_py_exception(const std::string& what)
{
    auto err = PyErr_Occurred();
    if (err != nullptr) {

        PyObject *pExcType, *pExcValue, *pExcTraceback;
        PyErr_Fetch(&pExcType, &pExcValue, &pExcTraceback);

        std::ostringstream oss;
        oss << "Fatal py exception encountered: ";
        oss << what << "\n";
        if (pExcValue != nullptr) {
            PyObject* pRepr = PyObject_Repr(pExcValue);
            oss << PyBytes_AsString(PyUnicode_AsEncodedString(pRepr, "utf-8", nullptr));
            Py_DECREF(pRepr);
        } else {
            oss << "unknown error";
        }

        PyErr_Clear();

        Py_XDECREF(pExcType);
        Py_XDECREF(pExcValue);
        Py_XDECREF(pExcTraceback);

        auto msg = oss.str();
        std::cerr << msg << std::endl;
        throw cppfmu::FatalError(msg.c_str());
    }
}

} // namespace pythonfmu

#endif
