
#ifndef PYTHONFMU_PYTHONSTATE_HPP
#define PYTHONFMU_PYTHONSTATE_HPP

#include <Python.h>
#include <iostream>

#include "callbacks.cpp"

namespace pythonfmu
{

class PyState
{
public:
    PyState()
    {
        std::string module_name = "fmi2facade";
        was_initialized_ = Py_IsInitialized();

        if (!was_initialized_) {
            PyImport_AppendInittab(module_name.c_str(), &PyInit_emb);
            Py_SetProgramName(L"./PythonFMU");
            Py_Initialize();
            PyEval_InitThreads();
            _mainPyThread = PyEval_SaveThread();
        } else {
            PyGILState_STATE gil_state = PyGILState_Ensure();

            PyImport_AddModule(module_name.c_str());
            PyObject* pyModule = PyInit_emb();
            PyObject* sys_modules = PyImport_GetModuleDict();
            PyDict_SetItemString(sys_modules, module_name.c_str(), pyModule);
            Py_DECREF(pyModule);

            PyGILState_Release(gil_state);
        }
    }

    ~PyState()
    {
        if (!was_initialized_) {
            PyEval_RestoreThread(_mainPyThread);
            Py_Finalize();
        }
    }

private:
    bool was_initialized_;
    PyThreadState* _mainPyThread;
};

} // namespace pythonfmu

#endif //PYTHONFMU_PYTHONSTATE_HPP
