
#include <pythonfmu/PyObjectWrapper.hpp>

#include <iostream>
#include <sstream>
#include <utility>
#include <fstream>

namespace pythonfmu
{

PyObjectWrapper::PyObjectWrapper(const std::string& resources)
{
    std::string scriptModule;
    std::ifstream infile(resources + "/slavemodule.txt");
    std::getline(infile, scriptModule);

    std::ostringstream oss;
    oss << "import sys\n";
    oss << "sys.path.append(r'" << resources << "')\n";

    PyRun_SimpleString(oss.str().c_str());

    pModule_ = PyImport_ImportModule(scriptModule.c_str());
    pClass_ = PyObject_GetAttrString(pModule_, "Model");
    pInstance_ = PyObject_CallFunctionObjArgs(pClass_, nullptr);

    auto f = PyObject_CallMethod(pInstance_, "define", nullptr);
    Py_XDECREF(f);
}

void PyObjectWrapper::setupExperiment(double startTime)
{
    auto f = PyObject_CallMethod(pInstance_, "setupExperiment", "(d)", startTime);
    Py_XDECREF(f);
}

void PyObjectWrapper::enterInitializationMode()
{
    auto f = PyObject_CallMethod(pInstance_, "enterInitializationMode", nullptr);
    Py_XDECREF(f);
}

void PyObjectWrapper::exitInitializationMode()
{
    auto f = PyObject_CallMethod(pInstance_, "exitInitializationMode", nullptr);
    Py_XDECREF(f);
}

bool PyObjectWrapper::doStep(double currentTime, double stepSize)
{
    auto pyStatus = PyObject_CallMethod(pInstance_, "doStep", "(dd)", currentTime, stepSize);
    bool status = static_cast<bool>(PyObject_IsTrue(pyStatus));
    Py_XDECREF(pyStatus);
    return status;
}

void PyObjectWrapper::reset()
{
    auto f = PyObject_CallMethod(pInstance_, "reset", nullptr);
    Py_XDECREF(f);
}

void PyObjectWrapper::terminate()
{
    auto f = PyObject_CallMethod(pInstance_, "terminate", nullptr);
    Py_XDECREF(f);
}

void PyObjectWrapper::getInteger(const cppfmu::FMIValueReference* vr, std::size_t nvr, cppfmu::FMIInteger* values)
{
    PyObject* vrs = PyList_New(nvr);
    PyObject* refs = PyList_New(nvr);
    for (int i = 0; i < nvr; i++) {
        PyList_SetItem(vrs, i, Py_BuildValue("i", vr[i]));
        PyList_SetItem(refs, i, Py_BuildValue("i", 0));
    }
    auto f = PyObject_CallMethod(pInstance_, "getInteger", "(OO)", vrs, refs);
    Py_XDECREF(f);

    for (int i = 0; i < nvr; i++) {
        PyObject* value = PyList_GetItem(refs, i);
        values[i] = static_cast<int>(PyLong_AsLong(value));
        Py_DECREF(value);
    }

    Py_XDECREF(vrs);
    Py_XDECREF(refs);
}

void PyObjectWrapper::getReal(const cppfmu::FMIValueReference* vr, std::size_t nvr, cppfmu::FMIReal* values)
{
    PyObject* vrs = PyList_New(nvr);
    PyObject* refs = PyList_New(nvr);
    for (int i = 0; i < nvr; i++) {
        PyList_SetItem(vrs, i, Py_BuildValue("i", vr[i]));
        PyList_SetItem(refs, i, Py_BuildValue("d", 0.0));
    }

    auto f = PyObject_CallMethod(pInstance_, "getReal", "(OO)", vrs, refs);
    Py_XDECREF(f);

    for (int i = 0; i < nvr; i++) {
        PyObject* value = PyList_GetItem(refs, i);
        values[i] = PyFloat_AsDouble(value);
        Py_DECREF(value);
    }

    Py_DECREF(vrs);
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

    auto f = PyObject_CallMethod(pInstance_, "setInteger", "(OO)", vrs, refs);
    Py_XDECREF(f);

    Py_DECREF(vrs);
    Py_DECREF(refs);
}

void PyObjectWrapper::setReal(const cppfmu::FMIValueReference* vr, std::size_t nvr, const cppfmu::FMIReal* values)
{
    PyObject* vrs = PyList_New(nvr);
    PyObject* refs = PyList_New(nvr);
    for (int i = 0; i < nvr; i++) {
        PyList_SetItem(vrs, i, Py_BuildValue("i", vr[i]));
        PyList_SetItem(refs, i, Py_BuildValue("d", values[i]));
    }

    auto f = PyObject_CallMethod(pInstance_, "setReal", "(OO)", vrs, refs);
    Py_XDECREF(f);

    Py_DECREF(vrs);
    Py_DECREF(refs);
}


PyObjectWrapper::~PyObjectWrapper()
{
    Py_XDECREF(pInstance_);
    Py_XDECREF(pClass_);
    Py_DECREF(pModule_);
}

} // namespace pythonfmu
