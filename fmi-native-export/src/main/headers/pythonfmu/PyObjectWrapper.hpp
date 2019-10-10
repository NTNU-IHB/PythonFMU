
#ifndef PYTHONFMU_PYOBJECTWRAPPER_HPP
#define PYTHONFMU_PYOBJECTWRAPPER_HPP

#include <pythonfmu/thread_worker.hpp>

#include <Python.h>

namespace pythonfmu
{

class PyObjectWrapper
{

public:
    PyObjectWrapper(const std::string& resources);

    void setupExperiment(double startTime);

    void enterInitializationMode();

    void exitInitializationMode();

    bool doStep(double currentTime, double steSize);

    void reset();

    void terminate();

    ~PyObjectWrapper();

private:
    PyObject* pModule_;
    PyObject* pClass_;
    PyObject* pInstance_;
};

} // namespace pythonfmu

#endif //PYTHONFMU_PYOBJECTWRAPPER_HPP
