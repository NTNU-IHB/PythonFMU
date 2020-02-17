
#ifndef PYTHONFMU_PYTHONSTATE_HPP
#define PYTHONFMU_PYTHONSTATE_HPP

#include <Python.h>
#include <functional>
#include <iostream>

namespace pythonfmu
{

class PyState
{
public:
    static volatile bool was_initialized_;

    PyState()
    {
        was_initialized_ = Py_IsInitialized();

        if (!was_initialized_) {
            Py_Initialize();
        }
    }

    static inline void run(const std::function<void()>& f)
    {
        if (!was_initialized_) {
            f();
        } else {
            PyGILState_STATE gil_state = PyGILState_Ensure();
            f();
            PyGILState_Release(gil_state);
        }
    }

    ~PyState()
    {
        if (!was_initialized_) {
            Py_Finalize();
        }
    }

};

volatile bool PyState::was_initialized_ = false;

} // namespace pythonfmu

#endif //PYTHONFMU_PYTHONSTATE_HPP
