
#ifndef PYTHONFMU_PYTHONSTATE_HPP
#define PYTHONFMU_PYTHONSTATE_HPP

#include "IPyState.hpp"
#include <Python.h>
#include <condition_variable>
#include <iostream>
#include <mutex>
#include <thread>

namespace pythonfmu
{
    class PyState : public IPyState
    {
    public:
        PyState()
            : _initDeinitPyThread_{ &PyState::Worker, this }
        {
            auto lock = std::unique_lock{ mutex_ };
            conditionalVariable_.wait(lock, [&] { return consructed_; });
        }

        ~PyState() override
        {
            {
                auto const lock = std::lock_guard{ mutex_ };
                destroyRequested_ = true;
            }
            conditionalVariable_.notify_one();
            if (_initDeinitPyThread_.joinable()) _initDeinitPyThread_.join();
        }

    private:

        // In accordance to the documentation https://docs.python.org/3/c-api/init.html#c.Py_FinalizeEx 
        // the Py_Initialize/Py_Finalize should be called from the same
        // thread. The FMI standard allows to call fmi functions from different threads, also different threads
        // could be used for loading unloading the FMU libraries. There is a deadlock, when the simulation tool 
        // unloads the FMU library from the thread which is differs from the thread where the Py_Initialize was called.
        // Create a new thread which is used for calling Py_Initialize and Py_Deinitialize. The thread waits for
        // notification from destructor and then calls Py_Deinitialize.

        void Worker()
        {
            // It will be nullptr in case when some other tool already called Py_IsInitialized.
            // There is no need to call Py_Finalize thus, this thread can exit ASAP.
            auto const mainPyThread = []() -> PyThreadState* {
                auto const justInitialized = !Py_IsInitialized();
                if (justInitialized) {
                    Py_SetProgramName(L"./PythonFMU");
                    Py_Initialize();
#if PY_VERSION_HEX < 0x03070000
                    PyEval_InitThreads();
#endif
                    return PyEval_SaveThread();
                }
                return nullptr;
                }();

                {
                    auto const lock = std::lock_guard{ mutex_ };
                    consructed_ = true;
                }
                conditionalVariable_.notify_one();

                if (nullptr != mainPyThread) {
                    auto lock = std::unique_lock{ mutex_ };
                    conditionalVariable_.wait(lock, [&] { return destroyRequested_; });

                    PyEval_RestoreThread(mainPyThread);
                    Py_Finalize();
                }
        }

        bool consructed_ = false;
        bool destroyRequested_ = false;
        std::condition_variable conditionalVariable_;
        std::mutex mutex_;
        std::thread _initDeinitPyThread_;
    };

} // namespace pythonfmu

#endif //PYTHONFMU_PYTHONSTATE_HPP