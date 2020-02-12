
#include "pythonfmu/PyObjectWrapper.hpp"

#include "pythonfmu/PyException.hpp"

#include "cppfmu/cppfmu_common.hpp"

#include <fstream>
#include <iostream>
#include <sstream>
#include <utility>

namespace
{

inline std::string getline(const std::string& fileName)
{
    std::string line;
    std::ifstream infile(fileName);
    std::getline(infile, line);
    return line;
}

} // namespace

namespace pythonfmu
{

PyObjectWrapper::PyObjectWrapper(const std::string& instanceName, const std::string& resources)
    : instanceName_(instanceName)
{
    // Append resources path to python sys path
    PyObject* sys_module = PyImport_ImportModule("sys");
    if (sys_module == nullptr) {
        handle_py_exception("[ctor] PyImport_ImportModule");
    }
    PyObject* sys_path = PyObject_GetAttrString(sys_module, "path");
    Py_DECREF(sys_module);
    if (sys_path == nullptr) {
        handle_py_exception("[ctor] PyObject_GetAttrString");
    }
    int success = PyList_Insert(sys_path, 0, PyUnicode_FromString(resources.c_str()));
    Py_DECREF(sys_path);
    if (success != 0) {
        handle_py_exception("[ctor] PyList_Insert");
    }

    auto moduleName = getline(resources + "/slavemodule.txt");
    PyObject* pModule = PyImport_ImportModule(moduleName.c_str());
    if (pModule == nullptr) {
        handle_py_exception("[ctor] PyImport_ImportModule");
    }

    PyObject* className = PyObject_GetAttrString(pModule, "slave_class");
    if (className == nullptr) {
        handle_py_exception("[ctor] PyObject_GetAttrString");
    }

    PyObject* pClass = PyObject_GetAttr(pModule, className);
    Py_DECREF(pModule);
    Py_DECREF(className);
    if (pClass == nullptr) {
        handle_py_exception("[ctor] PyObject_GetAttr");
    }
    PyObject *argList = Py_BuildValue("s", instanceName.c_str());
    pInstance_ = PyObject_CallFunctionObjArgs(pClass, argList, nullptr);
    Py_DECREF(argList);
    Py_DECREF(pClass);
    if (pInstance_ == nullptr) {
        handle_py_exception("[ctor] PyObject_CallFunctionObjArgs");
    }
}

void PyObjectWrapper::setupExperiment(double startTime)
{
    auto f = PyObject_CallMethod(pInstance_, "setup_experiment", "(d)", startTime);
    if (f == nullptr) {
        handle_py_exception("[setupExperiment] PyObject_CallMethod");
    }
    Py_DECREF(f);
}

void PyObjectWrapper::enterInitializationMode()
{
    auto f = PyObject_CallMethod(pInstance_, "enter_initialization_mode", nullptr);
    if (f == nullptr) {
        handle_py_exception("[enterInitializationMode] PyObject_CallMethod");
    }
    Py_DECREF(f);
}

void PyObjectWrapper::exitInitializationMode()
{
    auto f = PyObject_CallMethod(pInstance_, "exit_initialization_mode", nullptr);
    if (f == nullptr) {
        handle_py_exception("[exitInitializationMode] PyObject_CallMethod");
    }
    Py_DECREF(f);
}

bool PyObjectWrapper::doStep(double currentTime, double stepSize)
{
    auto f = PyObject_CallMethod(pInstance_, "do_step", "(dd)", currentTime, stepSize);
    if (f == nullptr) {
        handle_py_exception("[doStep] PyObject_CallMethod");
    }
    bool status = static_cast<bool>(PyObject_IsTrue(f));
    Py_DECREF(f);
    return status;
}

void PyObjectWrapper::reset()
{
    auto f = PyObject_CallMethod(pInstance_, "reset", nullptr);
    if (f == nullptr) {
        handle_py_exception("[reset] PyObject_CallMethod");
    }
    Py_DECREF(f);
}

void PyObjectWrapper::terminate()
{
    auto f = PyObject_CallMethod(pInstance_, "terminate", nullptr);
    if (f == nullptr) {
        handle_py_exception("[terminate] PyObject_CallMethod");
    }
    Py_DECREF(f);
}

void PyObjectWrapper::getInteger(const cppfmu::FMIValueReference* vr, std::size_t nvr, cppfmu::FMIInteger* values) const
{
    PyObject* vrs = PyList_New(nvr);
    for (int i = 0; i < nvr; i++) {
        PyList_SetItem(vrs, i, Py_BuildValue("i", vr[i]));
    }
    auto refs = PyObject_CallMethod(pInstance_, "get_integer", "O", vrs);
    Py_DECREF(vrs);
    if (refs == nullptr) {
        handle_py_exception("[getInteger] PyObject_CallMethod");
    }

    for (int i = 0; i < nvr; i++) {
        PyObject* value = PyList_GetItem(refs, i);
        values[i] = static_cast<cppfmu::FMIInteger>(PyLong_AsLong(value));
    }
    Py_DECREF(refs);
}

void PyObjectWrapper::getReal(const cppfmu::FMIValueReference* vr, std::size_t nvr, cppfmu::FMIReal* values) const
{
    PyObject* vrs = PyList_New(nvr);
    for (int i = 0; i < nvr; i++) {
        PyList_SetItem(vrs, i, Py_BuildValue("i", vr[i]));
    }

    auto refs = PyObject_CallMethod(pInstance_, "get_real", "O", vrs);
    Py_DECREF(vrs);
    if (refs == nullptr) {
        handle_py_exception("[getReal] PyObject_CallMethod");
    }

    for (int i = 0; i < nvr; i++) {
        PyObject* value = PyList_GetItem(refs, i);
        values[i] = PyFloat_AsDouble(value);
    }
    Py_DECREF(refs);
}

void PyObjectWrapper::getBoolean(const cppfmu::FMIValueReference* vr, std::size_t nvr, cppfmu::FMIBoolean* values) const
{
    PyObject* vrs = PyList_New(nvr);
    for (int i = 0; i < nvr; i++) {
        PyList_SetItem(vrs, i, Py_BuildValue("i", vr[i]));
    }
    auto refs = PyObject_CallMethod(pInstance_, "get_boolean", "O", vrs);
    Py_DECREF(vrs);
    if (refs == nullptr) {
        handle_py_exception("[getBoolean] PyObject_CallMethod");
    }

    for (int i = 0; i < nvr; i++) {
        PyObject* value = PyList_GetItem(refs, i);
        values[i] = PyObject_IsTrue(value);
    }
    Py_DECREF(refs);
}

void PyObjectWrapper::getString(const cppfmu::FMIValueReference* vr, std::size_t nvr, cppfmu::FMIString* values) const
{
    PyObject* vrs = PyList_New(nvr);
    for (int i = 0; i < nvr; i++) {
        PyList_SetItem(vrs, i, Py_BuildValue("i", vr[i]));
    }
    auto refs = PyObject_CallMethod(pInstance_, "get_string", "O", vrs);
    Py_DECREF(vrs);
    if (refs == nullptr) {
        handle_py_exception("[getString] PyObject_CallMethod");
    }

    for (int i = 0; i < nvr; i++) {
        PyObject* value = PyList_GetItem(refs, i);
        values[i] = PyBytes_AsString(PyUnicode_AsEncodedString(value, "utf-8", nullptr));
    }
    Py_DECREF(refs);
}

void PyObjectWrapper::setInteger(const cppfmu::FMIValueReference* vr, std::size_t nvr, const cppfmu::FMIInteger* values)
{
    PyObject* vrs = PyList_New(nvr);
    PyObject* refs = PyList_New(nvr);
    for (int i = 0; i < nvr; i++) {
        PyList_SetItem(vrs, i, Py_BuildValue("i", vr[i]));
        PyList_SetItem(refs, i, Py_BuildValue("i", values[i]));
    }

    auto f = PyObject_CallMethod(pInstance_, "set_integer", "(OO)", vrs, refs);
    Py_DECREF(vrs);
    Py_DECREF(refs);
    if (f == nullptr) {
        handle_py_exception("[setInteger] PyObject_CallMethod");
    }
    Py_DECREF(f);
}

void PyObjectWrapper::setReal(const cppfmu::FMIValueReference* vr, std::size_t nvr, const cppfmu::FMIReal* values)
{
    PyObject* vrs = PyList_New(nvr);
    PyObject* refs = PyList_New(nvr);
    for (int i = 0; i < nvr; i++) {
        PyList_SetItem(vrs, i, Py_BuildValue("i", vr[i]));
        PyList_SetItem(refs, i, Py_BuildValue("d", values[i]));
    }

    auto f = PyObject_CallMethod(pInstance_, "set_real", "(OO)", vrs, refs);
    Py_DECREF(vrs);
    Py_DECREF(refs);
    if (f == nullptr) {
        handle_py_exception("[setReal] PyObject_CallMethod");
    }
    Py_DECREF(f);
}

void PyObjectWrapper::setBoolean(const cppfmu::FMIValueReference* vr, std::size_t nvr, const cppfmu::FMIBoolean* values)
{
    PyObject* vrs = PyList_New(nvr);
    PyObject* refs = PyList_New(nvr);
    for (int i = 0; i < nvr; i++) {
        PyList_SetItem(vrs, i, Py_BuildValue("i", vr[i]));
        PyList_SetItem(refs, i, PyBool_FromLong(values[i]));
    }

    auto f = PyObject_CallMethod(pInstance_, "set_boolean", "(OO)", vrs, refs);
    Py_DECREF(vrs);
    Py_DECREF(refs);
    if (f == nullptr) {
        handle_py_exception("[setBoolean] PyObject_CallMethod");
    }
    Py_DECREF(f);
}

void PyObjectWrapper::setString(const cppfmu::FMIValueReference* vr, std::size_t nvr, const cppfmu::FMIString* value)
{
    PyObject* vrs = PyList_New(nvr);
    PyObject* refs = PyList_New(nvr);
    for (int i = 0; i < nvr; i++) {
        PyList_SetItem(vrs, i, Py_BuildValue("i", vr[i]));
        PyList_SetItem(refs, i, Py_BuildValue("s", value[i]));
    }

    auto f = PyObject_CallMethod(pInstance_, "set_string", "(OO)", vrs, refs);
    Py_DECREF(vrs);
    Py_DECREF(refs);
    if (f == nullptr) {
        handle_py_exception("[setString] PyObject_CallMethod");
    }
    Py_DECREF(f);
}

PyObjectWrapper::~PyObjectWrapper()
{
    Py_XDECREF(pInstance_);
}

} // namespace pythonfmu
