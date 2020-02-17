
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

        if (!_wasInitialized) {
            std::cout << "Initialize Python" << std::endl;
            Py_SetProgramName(L"./PythonFMU");
            Py_Initialize();
            PyEval_InitThreads();
            _mainPyThread = PyEval_SaveThread();
        }
    }

    ~PyState()
    {
        if (!_wasInitialized) {
            PyEval_RestoreThread(_mainPyThread);
            Py_Finalize();
        }
    }

private:
    bool _wasInitialized;
    PyThreadState* _mainPyThread;
};

} // namespace pythonfmu

#endif //PYTHONFMU_PYTHONSTATE_HPP
