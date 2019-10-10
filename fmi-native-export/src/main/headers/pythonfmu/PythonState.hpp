
#ifndef PYTHONFMU_PYTHONSTATE_HPP
#define PYTHONFMU_PYTHONSTATE_HPP

#include <Python.h>

namespace pythonfmu {

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

}

#endif //PYTHONFMU_PYTHONSTATE_HPP
