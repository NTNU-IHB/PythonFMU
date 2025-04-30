
#ifndef PYTHONFMU_PYSLAVEINSTANCE_HPP
#define PYTHONFMU_PYSLAVEINSTANCE_HPP

#include "pythonfmu/IPyState.hpp"
#include "pythonfmu/Logger.hpp"
#include "pythonfmu/SlaveInstance.hpp"

#include <Python.h>
#include <filesystem>
#include <string>
#include <vector>

namespace pythonfmu
{

struct fmu_data
{
    PyLogger* fmiLogger{nullptr};
    bool visible{false};
    std::string instanceName;
    std::string resourceLocation;
    std::shared_ptr<IPyState> pyState;
};

class PySlaveInstance : public SlaveInstance
{

public:
    PySlaveInstance(const fmu_data& data);

    void initialize(PyGILState_STATE gilState);

    void EnterInitializationMode() override;
    void ExitInitializationMode() override;
    void Terminate() override;
    void Reset() override;
    bool DoStep(fmi2Real currentCommunicationPoint, fmi2Real communicationStepSize, fmi2Boolean newStep, fmi2Real& endOfStep) override;

    void SetReal(const fmi2ValueReference* vr, std::size_t nvr, const fmi2Real* value) override;
    void SetInteger(const fmi2ValueReference* vr, std::size_t nvr, const fmi2Integer* value) override;
    void SetBoolean(const fmi2ValueReference* vr, std::size_t nvr, const fmi2Boolean* value) override;
    void SetString(const fmi2ValueReference* vr, std::size_t nvr, fmi2String const* value) override;

    void GetReal(const fmi2ValueReference* vr, std::size_t nvr, fmi2Real* value) const override;
    void GetInteger(const fmi2ValueReference* vr, std::size_t nvr, fmi2Integer* value) const override;
    void GetBoolean(const fmi2ValueReference* vr, std::size_t nvr, fmi2Boolean* value) const override;
    void GetString(const fmi2ValueReference* vr, std::size_t nvr, fmi2String* value) const override;

    void GetFMUstate(fmi2FMUstate& state) override;
    void SetFMUstate(const fmi2FMUstate& state) override;
    void FreeFMUstate(fmi2FMUstate& state) override;

    size_t SerializedFMUstateSize(const fmi2FMUstate& state) override;
    void SerializeFMUstate(const fmi2FMUstate& state, fmi2Byte bytes[], size_t size) override;
    void DeSerializeFMUstate(const fmi2Byte bytes[], size_t size, fmi2FMUstate& state) override;

    void clearLogBuffer() const;

    ~PySlaveInstance() override;

protected:
    fmu_data data_;
private:

    PyObject* pClass_;
    PyObject* pInstance_{};
    PyObject* pMessages_{};

    mutable std::vector<PyObject*> strBuffer;
    mutable std::vector<PyObject*> logStrBuffer;

    void handle_py_exception(const std::string& what, PyGILState_STATE gilState) const;

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
};

} // namespace pythonfmu

#endif
