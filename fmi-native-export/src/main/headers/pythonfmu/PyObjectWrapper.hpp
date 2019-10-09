
#ifndef PYTHONFMU_PYOBJECTWRAPPER_HPP
#define PYTHONFMU_PYOBJECTWRAPPER_HPP

#include <Python.h>

namespace pythonfmu
{

class PyObjectWrapper
{

public:
    PyObjectWrapper(PyObject* pModule, PyObject* pClass, PyObject* pInstance);

    ~PyObjectWrapper();

    void initialize();

    void setupExperiment(double startTime);

    void enterInitializationMode();

    void exitInitializationMode();

    bool doStep(double currentTime, double steSize);

    void terminate();

private:
    PyObject* pModule_;
    PyObject* pClass_;
    PyObject* pInstance_;
};

} // namespace pythonfmu

#endif //PYTHONFMU_PYOBJECTWRAPPER_HPP
