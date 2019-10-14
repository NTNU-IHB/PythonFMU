
#ifndef PYTHONFMU_PYTHONSTATE_HPP
#define PYTHONFMU_PYTHONSTATE_HPP

#include <Python.h>
#include <iostream>

namespace pythonfmu
{

class PythonState
{
public:
    PythonState()
    {
        Py_Initialize();
    }

    ~PythonState()
    {
        Py_FinalizeEx();
    }
};

} // namespace pythonfmu

#endif //PYTHONFMU_PYTHONSTATE_HPP
