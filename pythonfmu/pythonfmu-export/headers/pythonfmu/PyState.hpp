
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
        std::cout << "Creating PyState" << std::endl;
        _wasInitialized = Py_IsInitialized();
        std::cout << "PyEval_ThreadsInitialized " << PyEval_ThreadsInitialized() << std::endl;
        if(!_wasInitialized){
            std::cout << "Initialize Python" << std::endl;
            Py_SetProgramName(L"./PythonFMU");
            Py_Initialize();
        }
        std::cout << "Get main threads" << std::endl;
        PyThreadState *mainstate = PyThreadState_Get();

        std::cout << "Init threads" << std::endl;
        PyEval_InitThreads();
        PyEval_ReleaseThread(mainstate);
        // std::cout << "Get GIL" << std::endl;
        PyGILState_STATE gilstate = PyGILState_Ensure();

        PyThreadState_Swap(NULL);
        // std::cout << "New interpreter" << std::endl;
        _fmustate = Py_NewInterpreter();

        PyThreadState_Swap(mainstate);
        PyGILState_Release(gilstate);

        PyEval_RestoreThread(mainstate);
    }

    ~PyState()
    {
        std::cout << "Cleaning PyState" << std::endl;
        PyThreadState *mainstate = PyThreadState_Get();
        PyEval_InitThreads();
        PyEval_ReleaseThread(mainstate);
        PyGILState_STATE gilstate = PyGILState_Ensure();

        PyThreadState_Swap(_fmustate);
        Py_EndInterpreter(_fmustate);

        PyThreadState_Swap(mainstate);
        PyGILState_Release(gilstate);

        PyEval_RestoreThread(mainstate);

        if(!_wasInitialized){
            Py_Finalize();
        }
    }
private:
    bool _wasInitialized;
    PyThreadState *_fmustate;
};

} // namespace pythonfmu

#endif //PYTHONFMU_PYTHONSTATE_HPP
