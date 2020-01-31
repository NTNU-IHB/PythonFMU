

#include <fstream>
#include <iostream>
#include <sstream>
#include <utility>
#include "pythonfmu/PyException.hpp"
#include "pythonfmu/PyObjectWrapper.hpp"

#include "cppfmu/cppfmu_common.hpp"

namespace
{

inline std::string getline(const std::string& fileName)
{
    std::string line;
    std::ifstream infile(fileName);
    std::getline(infile, line);
    return line;
}

inline const char* get_class_name(PyObject* pModule) {
    auto f = PyObject_GetAttrString(pModule, "slave_class");
    if (f != nullptr) {
        return PyUnicode_AsUTF8(f);
    }
    return nullptr;
}

} // namespace

namespace pythonfmu
{

PyObjectWrapper::PyObjectWrapper(const std::string& resources)
{
    auto moduleName = getline(resources + "/slavemodule.txt");

    std::ostringstream oss;
    oss << "import sys\n";
    oss << "sys.path.append(r'" << resources << "')\n";
    PyRun_SimpleString(oss.str().c_str());

    pModule_ = PyImport_ImportModule(moduleName.c_str());
    if (pModule_ == nullptr) {
        handle_py_exception();
    }
    auto className = get_class_name(pModule_);
    if (className == nullptr) {
        handle_py_exception();
    }
    pClass_ = PyObject_GetAttrString(pModule_, className);
    if (pClass_ == nullptr) {
        handle_py_exception();
    }
    pInstance_ = PyObject_CallFunctionObjArgs(pClass_, nullptr);
    if (pInstance_ == nullptr) {
        handle_py_exception();
    }
}

void PyObjectWrapper::setupExperiment(double startTime)
{
    auto f = PyObject_CallMethod(pInstance_, "setup_experiment", "(d)", startTime);
    if (f == nullptr) {
        handle_py_exception();
    }
    Py_DECREF(f);
}

void PyObjectWrapper::enterInitializationMode()
{
    auto f = PyObject_CallMethod(pInstance_, "enter_initialization_mode", nullptr);
    if (f == nullptr) {
        handle_py_exception();
    }
    Py_DECREF(f);
}

void PyObjectWrapper::exitInitializationMode()
{
    auto f = PyObject_CallMethod(pInstance_, "exit_initialization_mode", nullptr);
    if (f == nullptr) {
        handle_py_exception();
    }
    Py_DECREF(f);
}

bool PyObjectWrapper::doStep(double currentTime, double stepSize)
{
    auto f = PyObject_CallMethod(pInstance_, "do_step", "(dd)", currentTime, stepSize);
    if (f == nullptr) {
        handle_py_exception();
    }
    bool status = static_cast<bool>(PyObject_IsTrue(f));
    Py_DECREF(f);
    return status;
}

void PyObjectWrapper::reset()
{
    auto f = PyObject_CallMethod(pInstance_, "reset", nullptr);
    if (f == nullptr) {
        handle_py_exception();
    }
    Py_DECREF(f);
}

void PyObjectWrapper::terminate()
{
    auto f = PyObject_CallMethod(pInstance_, "terminate", nullptr);
    if (f == nullptr) {
        handle_py_exception();
    }
    Py_DECREF(f);
}

void PyObjectWrapper::getInteger(const cppfmu::FMIValueReference* vr, std::size_t nvr, cppfmu::FMIInteger* values) const
{
    PyObject* vrs = PyList_New(nvr);
    PyObject* refs = PyList_New(nvr);
    for (int i = 0; i < nvr; i++) {
        PyList_SetItem(vrs, i, Py_BuildValue("i", vr[i]));
        PyList_SetItem(refs, i, Py_BuildValue("i", 0));
    }
    auto f = PyObject_CallMethod(pInstance_, "__get_integer__", "(OO)", vrs, refs);
    Py_DECREF(vrs);
    if (f == nullptr) {
        handle_py_exception();
    }
    Py_DECREF(f);

    for (int i = 0; i < nvr; i++) {
        PyObject* value = PyList_GetItem(refs, i);
        values[i] = static_cast<int>(PyLong_AsLong(value));
    }

    Py_DECREF(refs);
}

void PyObjectWrapper::getReal(const cppfmu::FMIValueReference* vr, std::size_t nvr, cppfmu::FMIReal* values) const
{
    PyObject* vrs = PyList_New(nvr);
    PyObject* refs = PyList_New(nvr);
    for (int i = 0; i < nvr; i++) {
        PyList_SetItem(vrs, i, Py_BuildValue("i", vr[i]));
        PyList_SetItem(refs, i, Py_BuildValue("d", 0.0));
    }

    auto f = PyObject_CallMethod(pInstance_, "__get_real__", "(OO)", vrs, refs);
    Py_DECREF(vrs);
    if (f == nullptr) {
        handle_py_exception();
    }
    Py_DECREF(f);

    for (int i = 0; i < nvr; i++) {
        PyObject* value = PyList_GetItem(refs, i);
        values[i] = PyFloat_AsDouble(value);
    }

    Py_DECREF(refs);
}

void PyObjectWrapper::getBoolean(const cppfmu::FMIValueReference* vr, std::size_t nvr, cppfmu::FMIBoolean* values) const
{
    PyObject* vrs = PyList_New(nvr);
    PyObject* refs = PyList_New(nvr);
    for (int i = 0; i < nvr; i++) {
        PyList_SetItem(vrs, i, Py_BuildValue("i", vr[i]));
        PyList_SetItem(refs, i, Py_BuildValue("i", 0));
    }
    auto f = PyObject_CallMethod(pInstance_, "__get_boolean__", "(OO)", vrs, refs);
    Py_DECREF(vrs);
    if (f == nullptr) {
        handle_py_exception();
    }
    Py_DECREF(f);

    for (int i = 0; i < nvr; i++) {
        PyObject* value = PyList_GetItem(refs, i);
        values[i] = PyObject_IsTrue(value);
    }

    Py_DECREF(refs);
}

void PyObjectWrapper::getString(const cppfmu::FMIValueReference* vr, std::size_t nvr, cppfmu::FMIString* values) const
{
    PyObject* vrs = PyList_New(nvr);
    PyObject* refs = PyList_New(nvr);
    for (int i = 0; i < nvr; i++) {
        PyList_SetItem(vrs, i, Py_BuildValue("i", vr[i]));
        PyList_SetItem(refs, i, Py_BuildValue("s", ""));
    }
    auto f = PyObject_CallMethod(pInstance_, "__get_string__", "(OO)", vrs, refs);
    Py_DECREF(vrs);
    if (f == nullptr) {
        handle_py_exception();
    }
    Py_DECREF(f);

    for (int i = 0; i < nvr; i++) {
        PyObject* value = PyList_GetItem(refs, i);
        values[i] = PyUnicode_AsUTF8(value);
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

    auto f = PyObject_CallMethod(pInstance_, "__set_integer__", "(OO)", vrs, refs);
    Py_DECREF(vrs);
    Py_DECREF(refs);
    if (f == nullptr) {
        handle_py_exception();
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

    auto f = PyObject_CallMethod(pInstance_, "__set_real__", "(OO)", vrs, refs);
    Py_DECREF(vrs);
    Py_DECREF(refs);
    if (f == nullptr) {
        handle_py_exception();
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

    auto f = PyObject_CallMethod(pInstance_, "__set_boolean__", "(OO)", vrs, refs);
    Py_DECREF(vrs);
    Py_DECREF(refs);
    if (f == nullptr) {
        handle_py_exception();
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

    auto f = PyObject_CallMethod(pInstance_, "__set_string__", "(OO)", vrs, refs);
    Py_DECREF(vrs);
    Py_DECREF(refs);
    if (f == nullptr) {
        handle_py_exception();
    }
    Py_DECREF(f);
}

PyObjectWrapper::~PyObjectWrapper()
{
    Py_XDECREF(pInstance_);
    Py_XDECREF(pClass_);
    Py_XDECREF(pModule_);
}

} // namespace pythonfmu
