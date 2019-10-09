
#include <pythonfmu/PyObjectWrapper.hpp>

namespace pythonfmu
{

PyObjectWrapper::PyObjectWrapper(PyObject* pModule, PyObject* pClass, PyObject* pInstance)
    : pModule_(pModule)
    , pClass_(pClass)
    , pInstance_(pInstance)
{}

void PyObjectWrapper::initialize()
{
    Py_XDECREF(PyObject_CallMethod(pInstance_, "initialize", nullptr));
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
    Py_XDECREF(PyObject_CallMethod(pInstance_, "setupExperiment", "(dd)", currentTime, stepSize));
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
