
#include "pythonfmu/PySlaveInstance.hpp"

#include "pythonfmu/PyException.hpp"
#include "pythonfmu/PyState.hpp"

#include "cppfmu/cppfmu_cs.hpp"

#include <fstream>
#include <iostream>
#include <sstream>
#include <utility>

namespace pythonfmu
{

inline std::string getLine(const std::string& fileName)
{
    std::string line;
    std::ifstream infile(fileName);
    std::getline(infile, line);
    return line;
}

PySlaveInstance::PySlaveInstance(const std::string& instanceName, const bool visible, const bool loggingOn, const std::string& resources)
    : visible_(visible), loggingOn_(loggingOn), instanceName_(instanceName)
{
    // Append resources path to python sys path
    PyObject* sys_module = PyImport_ImportModule("sys");
    if (sys_module == nullptr) {
        handle_py_exception("[ctor] PyImport_ImportModule");
    }
    PyObject* sys_path = PyObject_GetAttrString(sys_module, "path");
    Py_DECREF(sys_module);
    if (sys_path == nullptr) {
        handle_py_exception("[ctor] PyObject_GetAttrString");
    }
    int success = PyList_Insert(sys_path, 0, PyUnicode_FromString(resources.c_str()));
    Py_DECREF(sys_path);
    if (success != 0) {
        handle_py_exception("[ctor] PyList_Insert");
    }

    auto moduleName = getLine(resources + "/slavemodule.txt");
    pModule_ = PyImport_ImportModule(moduleName.c_str());
    if (pModule_ == nullptr) {
        handle_py_exception("[ctor] PyImport_ImportModule");
    }

}

void PySlaveInstance::initialize()
{
    Py_XDECREF(pInstance_);

    PyObject* className = PyObject_GetAttrString(pModule_, "slave_class");
    if (className == nullptr) {
        handle_py_exception("[ctor] PyObject_GetAttrString");
    }

    PyObject* pClass = PyObject_GetAttr(pModule_, className);
    Py_DECREF(className);
    if (pClass == nullptr) {
        handle_py_exception("[ctor] PyObject_GetAttr");
    }

    PyObject* args = PyTuple_New(0);
    PyObject* kwargs = Py_BuildValue("{sssi}", "instance_name", instanceName_.c_str(), "visible", visible_);
    pInstance_ = PyObject_Call(pClass, args, kwargs);
    Py_DECREF(args);
    Py_DECREF(kwargs);
    Py_DECREF(pClass);
    if (pInstance_ == nullptr) {
        handle_py_exception("[ctor] PyObject_Call");
    }
}

void PySlaveInstance::SetupExperiment(cppfmu::FMIBoolean, cppfmu::FMIReal, cppfmu::FMIReal startTime, cppfmu::FMIBoolean, cppfmu::FMIReal)
{
    auto f = PyObject_CallMethod(pInstance_, "setup_experiment", "(d)", startTime);
    if (f == nullptr) {
        handle_py_exception("[setupExperiment] PyObject_CallMethod");
    }
    Py_DECREF(f);
}

void PySlaveInstance::EnterInitializationMode()
{
    auto f = PyObject_CallMethod(pInstance_, "enter_initialization_mode", nullptr);
    if (f == nullptr) {
        handle_py_exception("[enterInitializationMode] PyObject_CallMethod");
    }
    Py_DECREF(f);
}

void PySlaveInstance::ExitInitializationMode()
{
    auto f = PyObject_CallMethod(pInstance_, "exit_initialization_mode", nullptr);
    if (f == nullptr) {
        handle_py_exception("[exitInitializationMode] PyObject_CallMethod");
    }
    Py_DECREF(f);
}

bool PySlaveInstance::DoStep(cppfmu::FMIReal currentTime, cppfmu::FMIReal stepSize, cppfmu::FMIBoolean, cppfmu::FMIReal& endOfStep)
{
    auto f = PyObject_CallMethod(pInstance_, "do_step", "(dd)", currentTime, stepSize);
    if (f == nullptr) {
        handle_py_exception("[doStep] PyObject_CallMethod");
    }
    bool status = static_cast<bool>(PyObject_IsTrue(f));
    Py_DECREF(f);
    return status;
}

void PySlaveInstance::Reset()
{
    auto f = PyObject_CallMethod(pInstance_, "reset", nullptr);
    if (f == nullptr) {
        handle_py_exception("[reset] PyObject_CallMethod");
    }
    Py_DECREF(f);
}

void PySlaveInstance::Terminate()
{
    auto f = PyObject_CallMethod(pInstance_, "terminate", nullptr);
    if (f == nullptr) {
        handle_py_exception("[terminate] PyObject_CallMethod");
    }
    Py_DECREF(f);
}

void PySlaveInstance::SetReal(const cppfmu::FMIValueReference* vr, std::size_t nvr, const cppfmu::FMIReal* values)
{
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
        handle_py_exception("[setReal] PyObject_CallMethod");
    }
    Py_DECREF(f);
}

void PySlaveInstance::SetInteger(const cppfmu::FMIValueReference* vr, std::size_t nvr, const cppfmu::FMIInteger* values)
{
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
        handle_py_exception("[setInteger] PyObject_CallMethod");
    }
    Py_DECREF(f);
}

void PySlaveInstance::SetBoolean(const cppfmu::FMIValueReference* vr, std::size_t nvr, const cppfmu::FMIBoolean* values)
{
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
        handle_py_exception("[setBoolean] PyObject_CallMethod");
    }
    Py_DECREF(f);
}

void PySlaveInstance::SetString(const cppfmu::FMIValueReference* vr, std::size_t nvr, cppfmu::FMIString const* values)
{
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
        handle_py_exception("[setString] PyObject_CallMethod");
    }
    Py_DECREF(f);
}

void PySlaveInstance::GetReal(const cppfmu::FMIValueReference* vr, std::size_t nvr, cppfmu::FMIReal* values) const
{
    PyObject* vrs = PyList_New(nvr);
    for (int i = 0; i < nvr; i++) {
        PyList_SetItem(vrs, i, Py_BuildValue("i", vr[i]));
    }

    auto refs = PyObject_CallMethod(pInstance_, "get_real", "O", vrs);
    Py_DECREF(vrs);
    if (refs == nullptr) {
        handle_py_exception("[getReal] PyObject_CallMethod");
    }

    for (int i = 0; i < nvr; i++) {
        PyObject* value = PyList_GetItem(refs, i);
        values[i] = PyFloat_AsDouble(value);
    }
    Py_DECREF(refs);
}

void PySlaveInstance::GetInteger(const cppfmu::FMIValueReference* vr, std::size_t nvr, cppfmu::FMIInteger* values) const
{
    PyObject* vrs = PyList_New(nvr);
    for (int i = 0; i < nvr; i++) {
        PyList_SetItem(vrs, i, Py_BuildValue("i", vr[i]));
    }
    auto refs = PyObject_CallMethod(pInstance_, "get_integer", "O", vrs);
    Py_DECREF(vrs);
    if (refs == nullptr) {
        handle_py_exception("[getInteger] PyObject_CallMethod");
    }

    for (int i = 0; i < nvr; i++) {
        PyObject* value = PyList_GetItem(refs, i);
        values[i] = static_cast<cppfmu::FMIInteger>(PyLong_AsLong(value));
    }
    Py_DECREF(refs);
}

void PySlaveInstance::GetBoolean(const cppfmu::FMIValueReference* vr, std::size_t nvr, cppfmu::FMIBoolean* values) const
{
    PyObject* vrs = PyList_New(nvr);
    for (int i = 0; i < nvr; i++) {
        PyList_SetItem(vrs, i, Py_BuildValue("i", vr[i]));
    }
    auto refs = PyObject_CallMethod(pInstance_, "get_boolean", "O", vrs);
    Py_DECREF(vrs);
    if (refs == nullptr) {
        handle_py_exception("[getBoolean] PyObject_CallMethod");
    }

    for (int i = 0; i < nvr; i++) {
        PyObject* value = PyList_GetItem(refs, i);
        values[i] = PyObject_IsTrue(value);
    }
    Py_DECREF(refs);
}

void PySlaveInstance::GetString(const cppfmu::FMIValueReference* vr, std::size_t nvr, cppfmu::FMIString* values) const
{
    PyObject* vrs = PyList_New(nvr);
    for (int i = 0; i < nvr; i++) {
        PyList_SetItem(vrs, i, Py_BuildValue("i", vr[i]));
    }
    auto refs = PyObject_CallMethod(pInstance_, "get_string", "O", vrs);
    Py_DECREF(vrs);
    if (refs == nullptr) {
        handle_py_exception("[getString] PyObject_CallMethod");
    }

    for (int i = 0; i < nvr; i++) {
        PyObject* value = PyList_GetItem(refs, i);
        values[i] = PyBytes_AsString(PyUnicode_AsEncodedString(value, "utf-8", nullptr));
    }
    Py_DECREF(refs);
}

void PySlaveInstance::GetFMUstate(fmi2FMUstate& state)
{
    auto f = PyObject_CallMethod(pInstance_, "_get_fmu_state", nullptr);
    if (f == nullptr) {
        handle_py_exception("[_get_fmu_state] PyObject_CallMethod");
    }
    state = reinterpret_cast<fmi2FMUstate*>(f);
}

void PySlaveInstance::SetFMUstate(const fmi2FMUstate& state)
{
    auto pyState = reinterpret_cast<PyObject*>(state);
    auto f = PyObject_CallMethod(pInstance_, "_set_fmu_state", "(O)", pyState);
    if (f == nullptr) {
        handle_py_exception("[_set_fmu_state] PyObject_CallMethod");
    }
}

void PySlaveInstance::FreeFMUstate(fmi2FMUstate& state)
{
    auto f = reinterpret_cast<PyObject*>(state);
    Py_XDECREF(f);
}

PySlaveInstance::~PySlaveInstance()
{
    Py_XDECREF(pModule_);
    Py_XDECREF(pInstance_);
}


} // namespace pythonfmu

std::unique_ptr<pythonfmu::PyState> pyState = nullptr;

cppfmu::UniquePtr<cppfmu::SlaveInstance> CppfmuInstantiateSlave(
    cppfmu::FMIString instanceName,
    cppfmu::FMIString,
    cppfmu::FMIString fmuResourceLocation,
    cppfmu::FMIString,
    cppfmu::FMIReal,
    cppfmu::FMIBoolean visible,
    cppfmu::FMIBoolean loggingOn,
    cppfmu::Memory memory,
    const cppfmu::Logger&)
{

    auto resources = std::string(fmuResourceLocation);
    auto find = resources.find("file://");

    if (find != std::string::npos) {
#ifdef _MSC_VER
        resources.replace(find, 8, "");
#else
        resources.replace(find, 7, "");
#endif
    }

    if (pyState == nullptr) {
        pyState = std::make_unique<pythonfmu::PyState>();
    }

    return cppfmu::AllocateUnique<pythonfmu::PySlaveInstance>(
        memory, instanceName, visible, loggingOn, resources);
}
