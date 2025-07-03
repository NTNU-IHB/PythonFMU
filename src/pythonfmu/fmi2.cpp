
#include "Logger.hpp"
#include "SlaveInstance.hpp"
#include "fmi/fmi2Functions.h"
#include "fmu_except.hpp"

#include <exception>
#include <limits>
#include <memory>
#include <optional>
#include <regex>

namespace
{

class Fmi2Logger : public pythonfmu::PyLogger
{

public:
    explicit Fmi2Logger(const std::string& instanceName, const fmi2CallbackFunctions* f)
        : PyLogger(instanceName)
        , f_(f)
    { }

protected:
    void debugLog(fmi2Status s, const std::string& category, const std::string& message) override
    {
        f_->logger(f_->componentEnvironment, instanceName_.c_str(),
            s, category.empty() ? nullptr : category.c_str(), message.c_str());
    }

private:
    const fmi2CallbackFunctions* f_;
};

// A struct that holds all the data for one model instance.
struct Fmi2Component
{

    Fmi2Component(std::unique_ptr<pythonfmu::SlaveInstance> slave, std::unique_ptr<Fmi2Logger> logger)
        : lastSuccessfulTime{std::numeric_limits<double>::quiet_NaN()}
        , slave(std::move(slave))
        , logger(std::move(logger))
    { }

    double lastSuccessfulTime{0};
    bool wantsToTerminate{false};

    std::unique_ptr<pythonfmu::SlaveInstance> slave;
    std::unique_ptr<Fmi2Logger> logger;
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


fmi2Component fmi2Instantiate(fmi2String instanceName,
    fmi2Type fmuType,
    fmi2String fmuGUID,
    fmi2String fmuResourceLocation,
    const fmi2CallbackFunctions* functions,
    fmi2Boolean visible,
    fmi2Boolean loggingOn)
{

    // Convert URI %20 to space
    auto resources = std::regex_replace(std::string(fmuResourceLocation), std::regex("%20"), " ");
    const auto find = resources.find("file://");

    if (find != std::string::npos) {
#ifdef _MSC_VER
        resources.replace(find, 8, "");
#else
        resources.replace(find, 7, "");
#endif
    }

    auto logger = std::make_unique<Fmi2Logger>(instanceName, functions);
    logger->setDebugLogging(loggingOn);

    try {

        auto instance = pythonfmu::createInstance(
            {logger.get(),
                visible == fmi2True,
                instanceName,
                resources,
                nullptr});

        auto component = std::make_unique<Fmi2Component>(std::move(instance), std::move(logger));
        return component.release();
    } catch (const std::exception& e) {
        logger->log(fmi2Fatal, e.what());
        return nullptr;
    }
}


void fmi2FreeInstance(fmi2Component c)
{
    if (c) {
        const auto component = static_cast<Fmi2Component*>(c);
        delete component;
    }
}


fmi2Status fmi2SetDebugLogging(
    fmi2Component c,
    fmi2Boolean loggingOn,
    size_t nCategories,
    const fmi2String categories[])
{
    const auto component = static_cast<Fmi2Component*>(c);

    std::vector<std::string> categoriesVec;
    if (nCategories > 0) {
        // Convert categories to std::vector<std::string>
        categoriesVec.reserve(nCategories);
        for (size_t i = 0; i < nCategories; ++i) {
            categoriesVec.emplace_back(categories[i]);
        }
    }

    component->logger->setDebugLogging(loggingOn, categoriesVec);

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
    const auto component = static_cast<Fmi2Component*>(c);
    try {
        component->slave->SetupExperiment(
            startTime,
            stopTimeDefined ? std::optional(stopTime) : std::nullopt,
            toleranceDefined ? std::optional(tolerance) : std::nullopt);
        return fmi2OK;
    } catch (const pythonfmu::fatal_error& e) {
        component->logger->log(fmi2Fatal, e.what());
        return fmi2Fatal;
    } catch (const std::exception& e) {
        component->logger->log(fmi2Error, e.what());
        return fmi2Error;
    }
}


fmi2Status fmi2EnterInitializationMode(fmi2Component c)
{
    const auto component = static_cast<Fmi2Component*>(c);
    try {
        component->slave->EnterInitializationMode();
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
    const auto component = static_cast<Fmi2Component*>(c);
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
    const auto component = static_cast<Fmi2Component*>(c);
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
    const auto component = static_cast<Fmi2Component*>(c);
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
    const auto component = static_cast<Fmi2Component*>(c);
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
    const auto component = static_cast<Fmi2Component*>(c);
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
    const auto component = static_cast<Fmi2Component*>(c);
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
    const auto component = static_cast<Fmi2Component*>(c);
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
    const auto component = static_cast<Fmi2Component*>(c);
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
    const auto component = static_cast<Fmi2Component*>(c);
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
    const auto component = static_cast<Fmi2Component*>(c);
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
    const auto component = static_cast<Fmi2Component*>(c);
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
    const auto component = static_cast<Fmi2Component*>(c);
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
    const auto component = static_cast<Fmi2Component*>(c);
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
    const auto component = static_cast<Fmi2Component*>(c);
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
    const auto component = static_cast<Fmi2Component*>(c);
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
    const auto component = static_cast<Fmi2Component*>(c);
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
    const auto component = static_cast<Fmi2Component*>(c);
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
    static_cast<Fmi2Component*>(c)->logger->log(
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
    static_cast<Fmi2Component*>(c)->logger->log(
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
    static_cast<Fmi2Component*>(c)->logger->log(
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
    const auto component = static_cast<Fmi2Component*>(c);
    try {
        double endTime = currentCommunicationPoint;
        const auto ok = component->slave->DoStep(
            currentCommunicationPoint,
            communicationStepSize);
        if (ok) {
            component->lastSuccessfulTime =
                currentCommunicationPoint + communicationStepSize;
            return fmi2OK;
        }

        component->lastSuccessfulTime = endTime;
        component->wantsToTerminate = true;
        return fmi2Discard;
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
    static_cast<Fmi2Component*>(c)->logger->log(
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
    static_cast<Fmi2Component*>(c)->logger->log(
        fmi2Error,
        "FMI function not supported: fmi2GetStatus");
    return fmi2Error;
}

fmi2Status fmi2GetRealStatus(
    fmi2Component c,
    const fmi2StatusKind s,
    fmi2Real* value)
{
    const auto component = static_cast<Fmi2Component*>(c);
    if (s == fmi2LastSuccessfulTime) {
        *value = component->lastSuccessfulTime;
        return fmi2OK;
    } else {
        component->logger->log(
            fmi2Discard,
            "Invalid status inquiry for fmi2GetRealStatus");
        return fmi2Discard;
    }
}

fmi2Status fmi2GetIntegerStatus(
    fmi2Component c,
    const fmi2StatusKind,
    fmi2Integer*)
{
    static_cast<Fmi2Component*>(c)->logger->log(
        fmi2Discard,
        "FMI function not supported: fmi2GetIntegerStatus");
    return fmi2Discard;
}

fmi2Status fmi2GetBooleanStatus(
    fmi2Component c,
    const fmi2StatusKind s,
    fmi2Boolean* value)
{
    const auto component = static_cast<Fmi2Component*>(c);
    if (s == fmi2Terminated) {
        *value = component->wantsToTerminate ? fmi2True : fmi2False;
        return fmi2OK;
    }
    component->logger->log(
        fmi2Discard, "FMI function not supported: fmi2GetBooleanStatus");
    return fmi2Discard;
}

fmi2Status fmi2GetStringStatus(
    fmi2Component c,
    const fmi2StatusKind,
    fmi2String*)
{
    static_cast<Fmi2Component*>(c)->logger->log(
        fmi2Discard, "FMI function not supported: fmi2GetStringStatus");
    return fmi2Discard;
}
}
