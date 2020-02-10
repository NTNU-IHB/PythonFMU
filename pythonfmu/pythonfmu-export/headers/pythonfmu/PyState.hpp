
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
        _wasInitialized = Py_IsInitialized();
        if(!_wasInitialized){
            Py_Initialize();
        }
    }

    ~PyState()
    {
        if(!_wasInitialized){
            Py_Finalize();
        }
    }
private:
    bool _wasInitialized;
};

} // namespace pythonfmu

#endif //PYTHONFMU_PYTHONSTATE_HPP
