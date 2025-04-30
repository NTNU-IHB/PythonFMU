
#include "Logger.hpp"
#include "PySlaveInstance.hpp"
#include "fmi/fmi2Functions.h"
#include "fmu_except.hpp"

#include <exception>
#include <limits>
#include <memory>
#include <optional>
#include <stdexcept>

namespace
{

class fmi2Logger : public pythonfmu::PyLogger
{

public:
    explicit fmi2Logger(const std::string& instanceName, const fmi2CallbackFunctions* f)
        : PyLogger(instanceName)
        , f_(f)
    { }

protected:
    void debugLog(fmi2Status s, const std::string& category, const std::string& message) override
    {
        f_->logger(f_->componentEnvironment, instanceName_.c_str(),
            s, category.empty() ? nullptr: category.c_str(), message.c_str());
    }

private:
    const fmi2CallbackFunctions* f_;
};

// A struct that holds all the data for one model instance.
struct Fmi2Component
{

    Fmi2Component(std::unique_ptr<pythonfmu::PySlaveInstance> slave, std::unique_ptr<fmi2Logger> logger)
        : lastSuccessfulTime{std::numeric_limits<double>::quiet_NaN()}
    , slave(std::move(slave))
    , logger(std::move(logger))
    { }

    double lastSuccessfulTime{0};

    std::unique_ptr<pythonfmu::PySlaveInstance> slave;
    std::unique_ptr<fmi2Logger> logger;

    double start{0};
    std::optional<double> stop;
    std::optional<double> tolerance;
};

} // namespace


// FMI functions
extern "C" {

// =============================================================================
// FMI 2.0 functions
// =============================================================================


const char* fmi2GetTypesPlatform()
{
    return fmi2TypesPlatform;
}


const char* fmi2GetVersion()
{
    return "2.0";
}


fmi2Component fmi2Instantiate(
    fmi2String instanceName,
    fmi2Type fmuType,
    fmi2String fmuGUID,
    fmi2String fmuResourceLocation,
    const fmi2CallbackFunctions* functions,
    fmi2Boolean visible,
    fmi2Boolean loggingOn)
{
//    try {
//        if (fmuType != fmi2CoSimulation) {
//            throw std::logic_error("Unsupported FMU instance type requested (only co-simulation is supported)");
//        }
//        auto component = std::make_unique<Fmi2Component>(cppfmu::Memory{*functions},
//            instanceName,
//            *functions,
//            loggingOn);
//        component->slave = CppfmuInstantiateSlave(
//            instanceName,
//            fmuGUID,
//            fmuResourceLocation,
//            "application/x-fmu-sharedlibrary",
//            0.0,
//            visible,
//            false,
//            component->memory,
//            component->logger);
//        return component.release();
//    } catch (const pythonfmu::fatal_error& e) {
//        functions->logger(functions->componentEnvironment, instanceName, fmi2Fatal, "", e.what());
//        return nullptr;
//    } catch (const std::exception& e) {
//        functions->logger(functions->componentEnvironment, instanceName, fmi2Error, "", e.what());
//        return nullptr;
//    }
}


void fmi2FreeInstance(fmi2Component c)
{
    const auto component = reinterpret_cast<Fmi2Component*>(c);
    delete component;
}


fmi2Status fmi2SetDebugLogging(
    fmi2Component c,
    fmi2Boolean loggingOn,
    size_t nCategories,
    const fmi2String categories[])
{
    const auto component = reinterpret_cast<Fmi2Component*>(c);

//    std::vector<cppfmu::String, cppfmu::Allocator<cppfmu::String>> newCategories(
//        cppfmu::Allocator<cppfmu::String>(component->memory));
//    for (size_t i = 0; i < nCategories; ++i) {
//        newCategories.push_back(cppfmu::CopyString(component->memory, categories[i]));
//    }
//
//    component->loggerSettings->debugLoggingEnabled = (loggingOn == fmi2True);
//    component->loggerSettings->loggedCategories.swap(newCategories);
    return fmi2OK;
}


fmi2Status fmi2SetupExperiment(
    fmi2Component c,
    fmi2Boolean toleranceDefined,
    fmi2Real tolerance,
    fmi2Real startTime,
    fmi2Boolean stopTimeDefined,
    fmi2Real stopTime)
{
    const auto component = reinterpret_cast<Fmi2Component*>(c);
    component->start = startTime;
    component->stop = stopTimeDefined ? std::optional<double>(stopTime) : std::nullopt;
    component->tolerance = toleranceDefined ? std::optional<double>(tolerance) : std::nullopt;
    
        return fmi2OK;
}


fmi2Status fmi2EnterInitializationMode(fmi2Component c)
{
    const auto component = reinterpret_cast<Fmi2Component*>(c);
    try {
        component->slave->EnterInitializationMode(component->start,
            component->stop,
            component->tolerance);
        return fmi2OK;
    } catch (const pythonfmu::fatal_error& e) {
        component->logger->log(fmi2Fatal, e.what());
        return fmi2Fatal;
    } catch (const std::exception& e) {
        component->logger->log(fmi2Error, e.what());
        return fmi2Error;
    }
}


fmi2Status fmi2ExitInitializationMode(fmi2Component c)
{
    const auto component = reinterpret_cast<Fmi2Component*>(c);
    try {
        component->slave->ExitInitializationMode();
        return fmi2OK;
    } catch (const pythonfmu::fatal_error& e) {
        component->logger->log(fmi2Fatal, e.what());
        return fmi2Fatal;
    } catch (const std::exception& e) {
        component->logger->log(fmi2Error, e.what());
        return fmi2Error;
    }
}


fmi2Status fmi2Terminate(fmi2Component c)
{
    const auto component = reinterpret_cast<Fmi2Component*>(c);
    try {
        component->slave->Terminate();
        return fmi2OK;
    } catch (const pythonfmu::fatal_error& e) {
        component->logger->log(fmi2Fatal, e.what());
        return fmi2Fatal;
    } catch (const std::exception& e) {
        component->logger->log(fmi2Error, e.what());
        return fmi2Error;
    }
}


fmi2Status fmi2Reset(fmi2Component c)
{
    const auto component = reinterpret_cast<Fmi2Component*>(c);
    try {
        component->slave->Reset();
        return fmi2OK;
    } catch (const pythonfmu::fatal_error& e) {
        component->logger->log(fmi2Fatal, e.what());
        return fmi2Fatal;
    } catch (const std::exception& e) {
        component->logger->log(fmi2Error, e.what());
        return fmi2Error;
    }
}


fmi2Status fmi2GetReal(
    fmi2Component c,
    const fmi2ValueReference vr[],
    size_t nvr,
    fmi2Real value[])
{
    const auto component = reinterpret_cast<Fmi2Component*>(c);
    try {
        component->slave->GetReal(vr, nvr, value);
        return fmi2OK;
    } catch (const pythonfmu::fatal_error& e) {
        component->logger->log(fmi2Fatal, e.what());
        return fmi2Fatal;
    } catch (const std::exception& e) {
        component->logger->log(fmi2Error, e.what());
        return fmi2Error;
    }
}

fmi2Status fmi2GetInteger(
    fmi2Component c,
    const fmi2ValueReference vr[],
    size_t nvr,
    fmi2Integer value[])
{
    const auto component = reinterpret_cast<Fmi2Component*>(c);
    try {
        component->slave->GetInteger(vr, nvr, value);
        return fmi2OK;
    } catch (const pythonfmu::fatal_error& e) {
        component->logger->log(fmi2Fatal, e.what());
        return fmi2Fatal;
    } catch (const std::exception& e) {
        component->logger->log(fmi2Error, e.what());
        return fmi2Error;
    }
}

fmi2Status fmi2GetBoolean(
    fmi2Component c,
    const fmi2ValueReference vr[],
    size_t nvr,
    fmi2Boolean value[])
{
    const auto component = reinterpret_cast<Fmi2Component*>(c);
    try {
        component->slave->GetBoolean(vr, nvr, value);
        return fmi2OK;
    } catch (const pythonfmu::fatal_error& e) {
        component->logger->log(fmi2Fatal, e.what());
        return fmi2Fatal;
    } catch (const std::exception& e) {
        component->logger->log(fmi2Error, e.what());
        return fmi2Error;
    }
}

fmi2Status fmi2GetString(
    fmi2Component c,
    const fmi2ValueReference vr[],
    size_t nvr,
    fmi2String value[])
{
    const auto component = reinterpret_cast<Fmi2Component*>(c);
    try {
        component->slave->GetString(vr, nvr, value);
        return fmi2OK;
    } catch (const pythonfmu::fatal_error& e) {
        component->logger->log(fmi2Fatal, e.what());
        return fmi2Fatal;
    } catch (const std::exception& e) {
        component->logger->log(fmi2Error, e.what());
        return fmi2Error;
    }
}


fmi2Status fmi2SetReal(
    fmi2Component c,
    const fmi2ValueReference vr[],
    size_t nvr,
    const fmi2Real value[])
{
    const auto component = reinterpret_cast<Fmi2Component*>(c);
    try {
        component->slave->SetReal(vr, nvr, value);
        return fmi2OK;
    } catch (const pythonfmu::fatal_error& e) {
        component->logger->log(fmi2Fatal, e.what());
        return fmi2Fatal;
    } catch (const std::exception& e) {
        component->logger->log(fmi2Error, e.what());
        return fmi2Error;
    }
}

fmi2Status fmi2SetInteger(
    fmi2Component c,
    const fmi2ValueReference vr[],
    size_t nvr,
    const fmi2Integer value[])
{
    const auto component = reinterpret_cast<Fmi2Component*>(c);
    try {
        component->slave->SetInteger(vr, nvr, value);
        return fmi2OK;
    } catch (const pythonfmu::fatal_error& e) {
        component->logger->log(fmi2Fatal, e.what());
        return fmi2Fatal;
    } catch (const std::exception& e) {
        component->logger->log(fmi2Error, e.what());
        return fmi2Error;
    }
}

fmi2Status fmi2SetBoolean(
    fmi2Component c,
    const fmi2ValueReference vr[],
    size_t nvr,
    const fmi2Boolean value[])
{
    const auto component = reinterpret_cast<Fmi2Component*>(c);
    try {
        component->slave->SetBoolean(vr, nvr, value);
        return fmi2OK;
    } catch (const pythonfmu::fatal_error& e) {
        component->logger->log(fmi2Fatal, e.what());
        return fmi2Fatal;
    } catch (const std::exception& e) {
        component->logger->log(fmi2Error, e.what());
        return fmi2Error;
    }
}

fmi2Status fmi2SetString(
    fmi2Component c,
    const fmi2ValueReference vr[],
    size_t nvr,
    const fmi2String value[])
{
    const auto component = reinterpret_cast<Fmi2Component*>(c);
    try {
        component->slave->SetString(vr, nvr, value);
        return fmi2OK;
    } catch (const pythonfmu::fatal_error& e) {
        component->logger->log(fmi2Fatal, e.what());
        return fmi2Fatal;
    } catch (const std::exception& e) {
        component->logger->log(fmi2Error, e.what());
        return fmi2Error;
    }
}


fmi2Status fmi2GetFMUstate(
    fmi2Component c,
    fmi2FMUstate* state)
{
    const auto component = reinterpret_cast<Fmi2Component*>(c);
    try {
        component->slave->GetFMUstate(*state);
        return fmi2OK;
    } catch (const pythonfmu::fatal_error& e) {
        component->logger->log(fmi2Fatal, e.what());
        return fmi2Fatal;
    } catch (const std::exception& e) {
        component->logger->log(fmi2Error, e.what());
        return fmi2Error;
    }
}

fmi2Status fmi2SetFMUstate(
    fmi2Component c,
    fmi2FMUstate state)
{
    const auto component = reinterpret_cast<Fmi2Component*>(c);
    try {
        component->slave->SetFMUstate(state);
        return fmi2OK;
    } catch (const pythonfmu::fatal_error& e) {
        component->logger->log(fmi2Fatal, e.what());
        return fmi2Fatal;
    } catch (const std::exception& e) {
        component->logger->log(fmi2Error, e.what());
        return fmi2Error;
    }
}

fmi2Status fmi2FreeFMUstate(
    fmi2Component c,
    fmi2FMUstate* state)
{
    const auto component = reinterpret_cast<Fmi2Component*>(c);
    try {
        component->slave->FreeFMUstate(*state);
        return fmi2OK;
    } catch (const pythonfmu::fatal_error& e) {
        component->logger->log(fmi2Fatal, e.what());
        return fmi2Fatal;
    } catch (const std::exception& e) {
        component->logger->log(fmi2Error, e.what());
        return fmi2Error;
    }
}

fmi2Status fmi2SerializedFMUstateSize(
    fmi2Component c,
    fmi2FMUstate state,
    size_t* size)
{
    const auto component = reinterpret_cast<Fmi2Component*>(c);
    try {
        *size = component->slave->SerializedFMUstateSize(state);
        return fmi2OK;
    } catch (const pythonfmu::fatal_error& e) {
        component->logger->log(fmi2Fatal, e.what());
        return fmi2Fatal;
    } catch (const std::exception& e) {
        component->logger->log(fmi2Error, e.what());
        return fmi2Error;
    }
}

fmi2Status fmi2SerializeFMUstate(
    fmi2Component c,
    fmi2FMUstate state,
    fmi2Byte bytes[],
    size_t size)
{
    const auto component = reinterpret_cast<Fmi2Component*>(c);
    try {
        component->slave->SerializeFMUstate(state, bytes, size);
        return fmi2OK;
    } catch (const pythonfmu::fatal_error& e) {
        component->logger->log(fmi2Fatal, e.what());
        return fmi2Fatal;
    } catch (const std::exception& e) {
        component->logger->log(fmi2Error, e.what());
        return fmi2Error;
    }
}

fmi2Status fmi2DeSerializeFMUstate(
    fmi2Component c,
    const fmi2Byte bytes[],
    size_t size,
    fmi2FMUstate* state)
{
    const auto component = reinterpret_cast<Fmi2Component*>(c);
    try {
        component->slave->DeSerializeFMUstate(bytes, size, *state);
        return fmi2OK;
    } catch (const pythonfmu::fatal_error& e) {
        component->logger->log(fmi2Fatal, e.what());
        return fmi2Fatal;
    } catch (const std::exception& e) {
        component->logger->log(fmi2Error, e.what());
        return fmi2Error;
    }
}


fmi2Status fmi2GetDirectionalDerivative(
    fmi2Component c,
    const fmi2ValueReference[],
    size_t,
    const fmi2ValueReference[],
    size_t,
    const fmi2Real[],
    fmi2Real[])
{
    reinterpret_cast<Fmi2Component*>(c)->logger->log(
        fmi2Error,
        "cppfmu",
        "FMI function not supported: fmi2GetDirectionalDerivative");
    return fmi2Error;
}

fmi2Status fmi2SetRealInputDerivatives(
    fmi2Component c,
    const fmi2ValueReference[],
    size_t,
    const fmi2Integer[],
    const fmi2Real[])
{
    reinterpret_cast<Fmi2Component*>(c)->logger->log(
        fmi2Error,
        "cppfmu",
        "FMI function not supported: fmi2SetRealInputDerivatives");
    return fmi2Error;
}

fmi2Status fmi2GetRealOutputDerivatives(
    fmi2Component c,
    const fmi2ValueReference[],
    size_t,
    const fmi2Integer[],
    fmi2Real[])
{
    reinterpret_cast<Fmi2Component*>(c)->logger->log(
        fmi2Error,
        "cppfmu",
        "FMI function not supported: fmiGetRealOutputDerivatives");
    return fmi2Error;
}

fmi2Status fmi2DoStep(
    fmi2Component c,
    fmi2Real currentCommunicationPoint,
    fmi2Real communicationStepSize,
    fmi2Boolean /*noSetFMUStatePriorToCurrentPoint*/)
{
    const auto component = reinterpret_cast<Fmi2Component*>(c);
    try {
        double endTime = currentCommunicationPoint;
        const auto ok = component->slave->DoStep(
            currentCommunicationPoint,
            communicationStepSize,
            fmi2True,
            endTime);
        if (ok) {
            component->lastSuccessfulTime =
                currentCommunicationPoint + communicationStepSize;
            return fmi2OK;
        } else {
            component->lastSuccessfulTime = endTime;
            return fmi2Discard;
        }
    } catch (const pythonfmu::fatal_error& e) {
        component->logger->log(fmi2Fatal, e.what());
        return fmi2Fatal;
    } catch (const std::exception& e) {
        component->logger->log(fmi2Error, e.what());
        return fmi2Error;
    }
}

fmi2Status fmi2CancelStep(fmi2Component c)
{
    reinterpret_cast<Fmi2Component*>(c)->logger->log(
        fmi2Error,
        "FMI function not supported: fmi2CancelStep");
    return fmi2Error;
}


/* Inquire slave status */
fmi2Status fmi2GetStatus(
    fmi2Component c,
    const fmi2StatusKind,
    fmi2Status*)
{
    reinterpret_cast<Fmi2Component*>(c)->logger->log(
        fmi2Error,
        "FMI function not supported: fmi2GetStatus");
    return fmi2Error;
}

fmi2Status fmi2GetRealStatus(
    fmi2Component c,
    const fmi2StatusKind s,
    fmi2Real* value)
{
    const auto component = reinterpret_cast<Fmi2Component*>(c);
    if (s == fmi2LastSuccessfulTime) {
        *value = component->lastSuccessfulTime;
        return fmi2OK;
    } else {
        component->logger->log(
            fmi2Error,
            "Invalid status inquiry for fmi2GetRealStatus");
        return fmi2Error;
    }
}

fmi2Status fmi2GetIntegerStatus(
    fmi2Component c,
    const fmi2StatusKind,
    fmi2Integer*)
{
    reinterpret_cast<Fmi2Component*>(c)->logger->log(
        fmi2Error,
        "FMI function not supported: fmi2GetIntegerStatus");
    return fmi2Error;
}

fmi2Status fmi2GetBooleanStatus(
    fmi2Component c,
    const fmi2StatusKind,
    fmi2Boolean*)
{
    reinterpret_cast<Fmi2Component*>(c)->logger->log(
        fmi2Error,"FMI function not supported: fmi2GetBooleanStatus");
    return fmi2Error;
}

fmi2Status fmi2GetStringStatus(
    fmi2Component c,
    const fmi2StatusKind,
    fmi2String*)
{
    reinterpret_cast<Fmi2Component*>(c)->logger->log(
        fmi2Error,"FMI function not supported: fmi2GetStringStatus");
    return fmi2Error;
}
}
