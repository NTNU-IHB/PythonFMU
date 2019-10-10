
#include <pythonfmu/PyObjectWrapper.hpp>

#include <iostream>
#include <sstream>
#include <utility>

namespace pythonfmu
{

PyObjectWrapper::PyObjectWrapper(const std::string& resources)
{

    std::ostringstream oss;
    oss << "import sys\n";
    oss << "sys.path.append(r'" << resources << "')\n";

    PyRun_SimpleString(oss.str().c_str());

    pModule_ = PyImport_ImportModule("model");
    pClass_ = PyObject_GetAttrString(pModule_, "Model");
    pInstance_ = PyObject_CallFunctionObjArgs(pClass_, nullptr);

    Py_XDECREF(PyObject_CallMethod(pInstance_, "define", nullptr));
}

void PyObjectWrapper::setupExperiment(double startTime)
{
    Py_XDECREF(PyObject_CallMethod(pInstance_, "setupExperiment", "(d)", startTime));
}

void PyObjectWrapper::enterInitializationMode()
{
    Py_XDECREF(PyObject_CallMethod(pInstance_, "enterInitializationMode", nullptr));
}

void PyObjectWrapper::exitInitializationMode()
{
    Py_XDECREF(PyObject_CallMethod(pInstance_, "exitInitializationMode", nullptr));
}

bool PyObjectWrapper::doStep(double currentTime, double stepSize)
{
    PyObject* pyStatus = PyObject_CallMethod(pInstance_, "doStep", "(dd)", currentTime, stepSize);
    bool status = static_cast<bool>(PyObject_IsTrue(pyStatus));
    Py_XDECREF(pyStatus);
    return status;
}

void PyObjectWrapper::reset()
{
    Py_XDECREF(PyObject_CallMethod(pInstance_, "reset", nullptr));
}

void PyObjectWrapper::terminate()
{
    Py_XDECREF(PyObject_CallMethod(pInstance_, "terminate", nullptr));
}

PyObjectWrapper::~PyObjectWrapper()
{
    Py_XDECREF(pInstance_);
    Py_XDECREF(pClass_);
    Py_DECREF(pModule_);
}

} // namespace pythonfmu
