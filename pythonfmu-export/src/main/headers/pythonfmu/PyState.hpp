
#ifndef PYTHONFMU_PYTHONSTATE_HPP
#define PYTHONFMU_PYTHONSTATE_HPP

#include <Python.h>
#include <iostream>

namespace pythonfmu
{

class PyState
{
public:
    PyState()
    {
        Py_Initialize();
    }

    ~PyState()
    {
        Py_Finalize();
    }
};

} // namespace pythonfmu

#endif //PYTHONFMU_PYTHONSTATE_HPP
