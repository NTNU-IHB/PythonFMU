
#include "fmu_except.hpp"

#include "pythonfmu/Logger.hpp"
#include "pythonfmu/PyState.hpp"
#include "pythonfmu/SlaveInstance.hpp"

#include <filesystem>
#include <fstream>
#include <functional>
#include <mutex>
#include <regex>
#include <sstream>
#include <string>
#include <utility>

using namespace pythonfmu;

namespace
{
std::string getline(const std::filesystem::path& fileName)
{
    std::string line;
    std::ifstream infile(fileName);
    std::getline(infile, line);
    return line;
}

PyObject* findClass(const std::string& resources, const std::string& moduleName)
{
    // Initialize the Python interpreter
    std::string filename = resources + "/" + moduleName + ".py";
    std::string deepestFile;
    int deepestChain = 0;

    // Read and execute the Python file
    std::ifstream file;
    file.open(filename);

    if (!file.is_open()) {
        return nullptr;
    }

    std::stringstream fileContents;
    std::string line;

    while (std::getline(file, line)) {
        fileContents << line << "\n";
    }

    // Compile python code so classes are added to the namespace
    PyObject* pyModule = PyImport_ImportModule(moduleName.c_str());

    if (pyModule == nullptr) {
        return nullptr;
    }
    PyObject* pGlobals = PyModule_GetDict(pyModule);
    PyObject* pLocals = PyDict_New();
    PyObject* pCode = Py_CompileString(fileContents.str().c_str(), moduleName.c_str(), Py_file_input);

    if (pCode != nullptr) {
        PyObject* pResult = PyEval_EvalCode(pCode, pGlobals, pLocals);
        Py_XDECREF(pResult);
    } else {
        PyErr_Print(); // Handle compilation error
        Py_Finalize();
        Py_DECREF(pGlobals);
        Py_DECREF(pyModule);
        Py_DECREF(pLocals);
        Py_DECREF(pCode);
        file.close();
        return nullptr;
    }

    fileContents.clear();
    PyObject *key, *value;
    Py_ssize_t pos = 0;

    while (PyDict_Next(pLocals, &pos, &key, &value)) {
        // Check if element in namespace is a class
        if (!PyType_Check(value)) {
            continue;
        }

        PyObject* pMroAttribute = PyObject_GetAttrString(value, "__mro__");

        if (pMroAttribute != nullptr && PySequence_Check(pMroAttribute)) {
            std::regex pattern("<class '[^']+\\.([^']+)'");
            PyObject* pMROList = PySequence_List(pMroAttribute);

            for (Py_ssize_t i = 0; i < PyList_Size(pMROList); ++i) {
                PyObject* pItem = PyList_GetItem(pMROList, i);
                std::smatch match;
                const char* className = PyBytes_AsString(PyUnicode_AsUTF8String(PyObject_Repr(pItem)));

                std::string str(className);
                const bool isMatch = std::regex_search(str, match, pattern);

                // If regex match is successfull, and found Fmi2Slave at the deepest level then update state
                if (isMatch && i > deepestChain && match[1] == "Fmi2Slave") {
                    deepestFile = PyBytes_AsString(PyUnicode_AsUTF8String(key));
                    deepestChain = i;
                }
            }
        }
        Py_DECREF(pMroAttribute);
    }

    PyObject* pyClassName = Py_BuildValue("s", deepestFile.c_str());
    PyObject* pyClass = PyObject_GetAttr(pyModule, pyClassName);

    // Clean up Python objects
    Py_DECREF(pCode);
    Py_DECREF(pLocals);
    Py_DECREF(pyModule);
    Py_DECREF(pGlobals);
    file.close();
    Py_DECREF(pyClassName);
    return pyClass;
}

void py_safe_run(const std::function<void(PyGILState_STATE gilState)>& f)
{
    PyGILState_STATE gil_state = PyGILState_Ensure();
    f(gil_state);
    PyGILState_Release(gil_state);
}

} // namespace

class PySlaveInstance : public SlaveInstance
{
public:
    explicit PySlaveInstance(fmu_data data)
        : data_(std::move(data))
    {
        py_safe_run([this](PyGILState_STATE gilState) {
            // Append resources path to python sys path
            PyObject* sys_module = PyImport_ImportModule("sys");
            if (sys_module == nullptr) {
                handle_py_exception("[ctor] PyImport_ImportModule", gilState);
            }
            PyObject* sys_path = PyObject_GetAttrString(sys_module, "path");
            Py_DECREF(sys_module);
            if (sys_path == nullptr) {
                handle_py_exception("[ctor] PyObject_GetAttrString", gilState);
            }
            int success = PyList_Insert(sys_path, 0, PyUnicode_FromString(resourceLocation().c_str()));

            Py_DECREF(sys_path);
            if (success != 0) {
                handle_py_exception("[ctor] PyList_Insert", gilState);
            }

            std::string moduleName = getline(resourceLocation() + "/slavemodule.txt");

            pClass_ = findClass(resourceLocation(), moduleName);
            if (pClass_ == nullptr) {
                handle_py_exception("[ctor] findClass", gilState);
            }

            initialize(gilState);
        });
    }

    void clearLogBuffer() const
    {
        clearLogStrBuffer();

        PyObject* msgField = Py_BuildValue("s", "msg");
        PyObject* categoryField = Py_BuildValue("s", "category");
        PyObject* statusField = Py_BuildValue("s", "status");

        if (pMessages_ != nullptr && PyList_Check(pMessages_)) {
            const auto size = PyList_Size(pMessages_);
            for (auto i = 0; i < size; i++) {
                PyObject* msg = PyList_GetItem(pMessages_, i);

                const auto msgAttr = PyObject_GetAttr(msg, msgField);
                const auto categoryAttr = PyObject_GetAttr(msg, categoryField);
                const auto statusAttr = PyObject_GetAttr(msg, statusField);

                const auto statusValue = static_cast<fmi2Status>(PyLong_AsLong(statusAttr));

                PyObject* msgValue = PyUnicode_AsEncodedString(msgAttr, "utf-8", nullptr);
                char* msgStr = PyBytes_AsString(msgValue);
                logStrBuffer.emplace_back(msgValue);

                const char* categoryStr = "";
                if (categoryAttr != Py_None) {
                    PyObject* categoryValue = PyUnicode_AsEncodedString(categoryAttr, "utf-8", nullptr);
                    categoryStr = PyBytes_AsString(categoryValue);
                    logStrBuffer.emplace_back(categoryValue);
                }


                log(statusValue, categoryStr, msgStr);
            }
            PyList_SetSlice(pMessages_, 0, size, nullptr);
        }

        Py_DECREF(msgField);
        Py_DECREF(categoryField);
        Py_DECREF(statusField);
    }

    void initialize(PyGILState_STATE gilState)
    {
        Py_XDECREF(pInstance_);
        Py_XDECREF(pMessages_);

        PyObject* args = PyTuple_New(0);
        PyObject* kwargs = Py_BuildValue("{ss,ss,sn,si}",
            "instance_name", data_.instanceName.c_str(),
            "resources", data_.resourceLocation.c_str(),
            "logger", data_.fmiLogger,
            "visible", data_.visible);
        pInstance_ = PyObject_Call(pClass_, args, kwargs);
        Py_DECREF(args);
        Py_DECREF(kwargs);
        if (pInstance_ == nullptr) {
            handle_py_exception("[initialize] PyObject_Call", gilState);
        }
        pMessages_ = PyObject_CallMethod(pInstance_, "_get_log_queue", nullptr);
    }

    void SetupExperiment(double startTime, std::optional<double> stop, std::optional<double> tolerance) override
    {
        py_safe_run([this, startTime](PyGILState_STATE gilState) {
            auto f = PyObject_CallMethod(pInstance_, "setup_experiment", "(d)", startTime);
            if (f == nullptr) {
                handle_py_exception("[setupExperiment] PyObject_CallMethod", gilState);
            }
            Py_DECREF(f);
            clearLogBuffer();
        });
    }

    void EnterInitializationMode() override
    {
        py_safe_run([this](PyGILState_STATE gilState) {
            auto f = PyObject_CallMethod(pInstance_, "enter_initialization_mode", nullptr);
            if (f == nullptr) {
                handle_py_exception("[enterInitializationMode] PyObject_CallMethod", gilState);
            }
            Py_DECREF(f);
            clearLogBuffer();
        });
    }

    void ExitInitializationMode() override
    {
        py_safe_run([this](PyGILState_STATE gilState) {
            auto f = PyObject_CallMethod(pInstance_, "exit_initialization_mode", nullptr);
            if (f == nullptr) {
                handle_py_exception("[exitInitializationMode] PyObject_CallMethod", gilState);
            }
            Py_DECREF(f);
            clearLogBuffer();
        });
    }

    bool Step(double currentTime, double stepSize) override
    {
        bool status;
        py_safe_run([this, &status, currentTime, stepSize](PyGILState_STATE gilState) {
            auto f = PyObject_CallMethod(pInstance_, "do_step", "(dd)", currentTime, stepSize);
            if (f == nullptr) {
                handle_py_exception("[doStep] PyObject_CallMethod", gilState);
            }
            status = static_cast<bool>(PyObject_IsTrue(f));
            Py_DECREF(f);
            clearLogBuffer();
        });

        return status;
    }

    void Reset() override
    {
        py_safe_run([this](PyGILState_STATE gilState) {
            initialize(gilState);
        });
    }

    void Terminate() override
    {
        py_safe_run([this](PyGILState_STATE gilState) {
            auto f = PyObject_CallMethod(pInstance_, "terminate", nullptr);
            if (f == nullptr) {
                handle_py_exception("[terminate] PyObject_CallMethod", gilState);
            }
            Py_DECREF(f);
            clearLogBuffer();
        });
    }

    void SetReal(const fmi2ValueReference* vr, std::size_t nvr, const fmi2Real* values) override
    {
        py_safe_run([this, &vr, nvr, &values](PyGILState_STATE gilState) {
            PyObject* vrs = PyList_New(nvr);
            PyObject* refs = PyList_New(nvr);
            for (int i = 0; i < nvr; i++) {
                PyList_SetItem(vrs, i, Py_BuildValue("i", vr[i]));
                PyList_SetItem(refs, i, Py_BuildValue("d", values[i]));
            }

            auto f = PyObject_CallMethod(pInstance_, "set_real", "(OO)", vrs, refs);
            Py_DECREF(vrs);
            Py_DECREF(refs);
            if (f == nullptr) {
                handle_py_exception("[setReal] PyObject_CallMethod", gilState);
            }
            Py_DECREF(f);
            clearLogBuffer();
        });
    }

    void SetInteger(const fmi2ValueReference* vr, std::size_t nvr, const fmi2Integer* values) override
    {
        py_safe_run([this, &vr, nvr, &values](PyGILState_STATE gilState) {
            PyObject* vrs = PyList_New(nvr);
            PyObject* refs = PyList_New(nvr);
            for (int i = 0; i < nvr; i++) {
                PyList_SetItem(vrs, i, Py_BuildValue("i", vr[i]));
                PyList_SetItem(refs, i, Py_BuildValue("i", values[i]));
            }

            auto f = PyObject_CallMethod(pInstance_, "set_integer", "(OO)", vrs, refs);
            Py_DECREF(vrs);
            Py_DECREF(refs);
            if (f == nullptr) {
                handle_py_exception("[setInteger] PyObject_CallMethod", gilState);
            }
            Py_DECREF(f);
            clearLogBuffer();
        });
    }

    void SetBoolean(const fmi2ValueReference* vr, std::size_t nvr, const fmi2Boolean* values) override
    {
        py_safe_run([this, &vr, nvr, &values](PyGILState_STATE gilState) {
            PyObject* vrs = PyList_New(nvr);
            PyObject* refs = PyList_New(nvr);
            for (int i = 0; i < nvr; i++) {
                PyList_SetItem(vrs, i, Py_BuildValue("i", vr[i]));
                PyList_SetItem(refs, i, PyBool_FromLong(values[i]));
            }

            auto f = PyObject_CallMethod(pInstance_, "set_boolean", "(OO)", vrs, refs);
            Py_DECREF(vrs);
            Py_DECREF(refs);
            if (f == nullptr) {
                handle_py_exception("[setBoolean] PyObject_CallMethod", gilState);
            }
            Py_DECREF(f);
            clearLogBuffer();
        });
    }

    void SetString(const fmi2ValueReference* vr, std::size_t nvr, fmi2String const* values) override
    {
        py_safe_run([this, &vr, nvr, &values](PyGILState_STATE gilState) {
            PyObject* vrs = PyList_New(nvr);
            PyObject* refs = PyList_New(nvr);
            for (int i = 0; i < nvr; i++) {
                PyList_SetItem(vrs, i, Py_BuildValue("i", vr[i]));
                PyList_SetItem(refs, i, Py_BuildValue("s", values[i]));
            }

            auto f = PyObject_CallMethod(pInstance_, "set_string", "(OO)", vrs, refs);
            Py_DECREF(vrs);
            Py_DECREF(refs);
            if (f == nullptr) {
                handle_py_exception("[setString] PyObject_CallMethod", gilState);
            }
            Py_DECREF(f);
            clearLogBuffer();
        });
    }

    void GetReal(const fmi2ValueReference* vr, std::size_t nvr, fmi2Real* values) const override
    {
        py_safe_run([this, &vr, nvr, &values](PyGILState_STATE gilState) {
            PyObject* vrs = PyList_New(nvr);
            for (int i = 0; i < nvr; i++) {
                PyList_SetItem(vrs, i, Py_BuildValue("i", vr[i]));
            }

            auto refs = PyObject_CallMethod(pInstance_, "get_real", "O", vrs);
            Py_DECREF(vrs);
            if (refs == nullptr) {
                handle_py_exception("[getReal] PyObject_CallMethod", gilState);
            }

            for (int i = 0; i < nvr; i++) {
                PyObject* value = PyList_GetItem(refs, i);
                values[i] = PyFloat_AsDouble(value);
            }
            Py_DECREF(refs);
            clearLogBuffer();
        });
    }

    void GetInteger(const fmi2ValueReference* vr, std::size_t nvr, fmi2Integer* values) const override
    {
        py_safe_run([this, &vr, nvr, &values](PyGILState_STATE gilState) {
            PyObject* vrs = PyList_New(nvr);
            for (int i = 0; i < nvr; i++) {
                PyList_SetItem(vrs, i, Py_BuildValue("i", vr[i]));
            }
            auto refs = PyObject_CallMethod(pInstance_, "get_integer", "O", vrs);
            Py_DECREF(vrs);
            if (refs == nullptr) {
                handle_py_exception("[getInteger] PyObject_CallMethod", gilState);
            }

            for (int i = 0; i < nvr; i++) {
                PyObject* value = PyList_GetItem(refs, i);
                values[i] = static_cast<fmi2Integer>(PyLong_AsLong(value));
            }
            Py_DECREF(refs);
            clearLogBuffer();
        });
    }

    void GetBoolean(const fmi2ValueReference* vr, std::size_t nvr, fmi2Boolean* values) const override
    {
        py_safe_run([this, &vr, nvr, &values](PyGILState_STATE gilState) {
            PyObject* vrs = PyList_New(nvr);
            for (int i = 0; i < nvr; i++) {
                PyList_SetItem(vrs, i, Py_BuildValue("i", vr[i]));
            }
            auto refs = PyObject_CallMethod(pInstance_, "get_boolean", "O", vrs);
            Py_DECREF(vrs);
            if (refs == nullptr) {
                handle_py_exception("[getBoolean] PyObject_CallMethod", gilState);
            }

            for (int i = 0; i < nvr; i++) {
                PyObject* value = PyList_GetItem(refs, i);
                values[i] = PyObject_IsTrue(value);
            }
            Py_DECREF(refs);
            clearLogBuffer();
        });
    }

    void GetString(const fmi2ValueReference* vr, std::size_t nvr, fmi2String* values) const override
    {
        py_safe_run([this, &vr, nvr, &values](PyGILState_STATE gilState) {
            clearStrBuffer();
            PyObject* vrs = PyList_New(nvr);
            for (int i = 0; i < nvr; i++) {
                PyList_SetItem(vrs, i, Py_BuildValue("i", vr[i]));
            }
            auto refs = PyObject_CallMethod(pInstance_, "get_string", "O", vrs);
            Py_DECREF(vrs);
            if (refs == nullptr) {
                handle_py_exception("[getString] PyObject_CallMethod", gilState);
            }

            for (int i = 0; i < nvr; i++) {
                PyObject* value = PyUnicode_AsEncodedString(PyList_GetItem(refs, i), "utf-8", nullptr);
                values[i] = PyBytes_AsString(value);
                strBuffer.emplace_back(value);
            }
            Py_DECREF(refs);
            clearLogBuffer();
        });
    }

    void GetFMUstate(fmi2FMUstate& state) override
    {
        py_safe_run([this, &state](PyGILState_STATE gilState) {
            auto f = PyObject_CallMethod(pInstance_, "_get_fmu_state", nullptr);
            if (f == nullptr) {
                handle_py_exception("[_get_fmu_state] PyObject_CallMethod", gilState);
            }
            state = reinterpret_cast<fmi2FMUstate*>(f);
            clearLogBuffer();
        });
    }

    void SetFMUstate(const fmi2FMUstate& state) override
    {
        py_safe_run([this, &state](PyGILState_STATE gilState) {
            auto pyState = reinterpret_cast<PyObject*>(state);
            auto f = PyObject_CallMethod(pInstance_, "_set_fmu_state", "(O)", pyState);
            if (f == nullptr) {
                handle_py_exception("[_set_fmu_state] PyObject_CallMethod", gilState);
            }
            clearLogBuffer();
        });
    }

    void FreeFMUstate(fmi2FMUstate& state) override
    {
        py_safe_run([this, &state](PyGILState_STATE gilState) {
            auto f = reinterpret_cast<PyObject*>(state);
            Py_XDECREF(f);
        });
    }

    size_t SerializedFMUstateSize(const fmi2FMUstate& state) override
    {
        size_t size;
        py_safe_run([this, &state, &size](PyGILState_STATE gilState) {
            auto pyState = reinterpret_cast<PyObject*>(state);
            PyObject* pyStateBytes = PyObject_CallMethod(pClass_, "_fmu_state_to_bytes", "(O)", pyState);
            if (pyStateBytes == nullptr) {
                handle_py_exception("[SerializedFMUstateSize] PyObject_CallMethod", gilState);
            }
            size = PyBytes_Size(pyStateBytes);
            Py_DECREF(pyStateBytes);
            clearLogBuffer();
        });
        return size;
    }

    void SerializeFMUstate(const fmi2FMUstate& state, fmi2Byte* bytes, size_t size) override
    {
        py_safe_run([this, &state, &bytes, size](PyGILState_STATE gilState) {
            auto pyState = reinterpret_cast<PyObject*>(state);
            PyObject* pyStateBytes = PyObject_CallMethod(pClass_, "_fmu_state_to_bytes", "(O)", pyState);
            if (pyStateBytes == nullptr) {
                handle_py_exception("[SerializeFMUstate] PyObject_CallMethod", gilState);
            }
            char* c = PyBytes_AsString(pyStateBytes);
            if (c == nullptr) {
                handle_py_exception("[SerializeFMUstate] PyBytes_AsString", gilState);
            }
            for (int i = 0; i < size; i++) {
                bytes[i] = c[i];
            }
            Py_DECREF(pyStateBytes);
            clearLogBuffer();
        });
    }

    void DeSerializeFMUstate(const fmi2Byte bytes[], size_t size, fmi2FMUstate& state) override
    {
        py_safe_run([this, &bytes, size, &state](PyGILState_STATE gilState) {
            PyObject* pyStateBytes = PyBytes_FromStringAndSize(bytes, size);
            if (pyStateBytes == nullptr) {
                handle_py_exception("[DeSerializeFMUstate] PyBytes_FromStringAndSize", gilState);
            }
            PyObject* pyState = PyObject_CallMethod(pClass_, "_fmu_state_from_bytes", "(O)", pyStateBytes);
            if (pyState == nullptr) {
                handle_py_exception("[DeSerializeFMUstate] PyObject_CallMethod", gilState);
            }
            state = reinterpret_cast<fmi2FMUstate*>(pyState);
            Py_DECREF(pyStateBytes);
            clearLogBuffer();
        });
    }

    ~PySlaveInstance() override
    {
        py_safe_run([this](PyGILState_STATE) {
            cleanPyObject();
        });
    }

private:
    fmu_data data_;

    PyObject* pClass_;
    PyObject* pInstance_{};
    PyObject* pMessages_{};

    mutable std::vector<PyObject*> strBuffer;
    mutable std::vector<PyObject*> logStrBuffer;

    std::string resourceLocation() const
    {
        return data_.resourceLocation;
    }

    void log(fmi2Status s, const std::string& message) const
    {
        data_.fmiLogger->log(s, message);
    }

    void log(fmi2Status s, const std::string& category, const std::string& message) const
    {
        data_.fmiLogger->log(s, category, message);
    }

    void clearStrBuffer() const
    {
        if (!strBuffer.empty()) {
            for (auto obj : strBuffer) {
                Py_DECREF(obj);
            }
            strBuffer.clear();
        }
    }

    void clearLogStrBuffer() const
    {
        if (!logStrBuffer.empty()) {
            for (auto obj : logStrBuffer) {
                Py_DECREF(obj);
            }
            logStrBuffer.clear();
        }
    }

    void cleanPyObject() const
    {
        clearLogBuffer();
        clearLogStrBuffer();
        clearStrBuffer();
        Py_XDECREF(pClass_);
        Py_XDECREF(pInstance_);
        Py_XDECREF(pMessages_);
    }


    void handle_py_exception(const std::string& what, PyGILState_STATE gilState) const
    {
        const auto err = PyErr_Occurred();
        if (err != nullptr) {
            cleanPyObject();

            PyObject *pExcType, *pExcValue, *pExcTraceback;
            PyErr_Fetch(&pExcType, &pExcValue, &pExcTraceback);

            std::ostringstream oss;
            oss << "Fatal py exception encountered: ";
            oss << what << "\n";
            if (pExcValue != nullptr) {
                PyObject* pRepr = PyObject_Repr(pExcValue);
                PyObject* pyStr = PyUnicode_AsEncodedString(pRepr, "utf-8", nullptr);
                oss << PyBytes_AsString(pyStr);
                Py_DECREF(pyStr);
                Py_DECREF(pRepr);
            } else {
                oss << "unknown error";
            }

            PyErr_Clear();

            Py_XDECREF(pExcType);
            Py_XDECREF(pExcValue);
            Py_XDECREF(pExcTraceback);

            PyGILState_Release(gilState);

            throw fatal_error(oss.str());
        }
    }
};

namespace
{

std::mutex pyStateMutex{};
std::shared_ptr<PyState> pyState{};

} // namespace

std::unique_ptr<SlaveInstance> pythonfmu::createInstance(fmu_data data)
{
    {
        auto const ensurePyStateAlive = [&]() {
            auto const lock = std::lock_guard{pyStateMutex};
            if (nullptr == pyState) pyState = std::make_shared<PyState>();
        };

        ensurePyStateAlive();
        auto c = std::make_unique<PySlaveInstance>(data);
        data.pyState = pyState;
        return c;
    }
}


extern "C" {

// The PyState instance owns it's own thread for constructing and destroying the Py* from the same thread.
// Creation of an std::thread increments ref counter of a shared library. So, when the client unloads the library
// the library won't be freed, as std::thread is alive, and the std::thread itself waits for de-initialization request.
// Thus, use DllMain on Windows and __attribute__((destructor)) on Linux for signaling to the PyState about de-initialization.
void finalizePythonInterpreter()
{
    pyState = nullptr;
}
}

namespace
{

#ifdef _WIN32
#    include <windows.h>

BOOL APIENTRY DllMain(HMODULE hModule,
    DWORD ul_reason_for_call,
    LPVOID lpReserved)
{
    switch (ul_reason_for_call) {
        case DLL_PROCESS_ATTACH:
            break;
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
            break;
        case DLL_PROCESS_DETACH:
            finalizePythonInterpreter();
            break;
    }
    return TRUE;
}
#elif defined(__linux__)
__attribute__((destructor)) void onLibraryUnload()
{
    finalizePythonInterpreter();
}
#else
#    error port the code
#endif
} // namespace
