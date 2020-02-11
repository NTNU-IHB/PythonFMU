
#include "pythonfmu/SlaveInstance.hpp"

#include "pythonfmu/PyState.hpp"

#include "cppfmu/cppfmu_cs.hpp"

namespace pythonfmu
{

SlaveInstance::SlaveInstance(const std::string& instanceName, const std::string& resources)
    : instance_(PyObjectWrapper(instanceName, resources))
{}

void SlaveInstance::SetupExperiment(cppfmu::FMIBoolean, cppfmu::FMIReal, cppfmu::FMIReal tStart, cppfmu::FMIBoolean, cppfmu::FMIReal)
{
    instance_.setupExperiment(tStart);
}

void SlaveInstance::EnterInitializationMode()
{
    instance_.enterInitializationMode();
}

void SlaveInstance::ExitInitializationMode()
{
    instance_.exitInitializationMode();
}

bool SlaveInstance::DoStep(cppfmu::FMIReal currentCommunicationPoint, cppfmu::FMIReal communicationStepSize, cppfmu::FMIBoolean, cppfmu::FMIReal& endOfStep)
{
    return instance_.doStep(currentCommunicationPoint, communicationStepSize);
}

void SlaveInstance::Reset()
{
    instance_.reset();
}

void SlaveInstance::Terminate()
{
    instance_.terminate();
}

void SlaveInstance::SetReal(const cppfmu::FMIValueReference* vr, std::size_t nvr, const cppfmu::FMIReal* value)
{
    instance_.setReal(vr, nvr, value);
}

void SlaveInstance::SetInteger(const cppfmu::FMIValueReference* vr, std::size_t nvr, const cppfmu::FMIInteger* value)
{
    instance_.setInteger(vr, nvr, value);
}

void SlaveInstance::SetBoolean(const cppfmu::FMIValueReference* vr, std::size_t nvr, const cppfmu::FMIBoolean* value)
{
    instance_.setBoolean(vr, nvr, value);
}

void SlaveInstance::SetString(const cppfmu::FMIValueReference* vr, std::size_t nvr, cppfmu::FMIString const* value)
{
    instance_.setString(vr, nvr, value);
}

void SlaveInstance::GetReal(const cppfmu::FMIValueReference* vr, std::size_t nvr, cppfmu::FMIReal* value) const
{
    instance_.getReal(vr, nvr, value);
}

void SlaveInstance::GetInteger(const cppfmu::FMIValueReference* vr, std::size_t nvr, cppfmu::FMIInteger* value) const
{
    instance_.getInteger(vr, nvr, value);
}

void SlaveInstance::GetBoolean(const cppfmu::FMIValueReference* vr, std::size_t nvr, cppfmu::FMIBoolean* value) const
{
    instance_.getBoolean(vr, nvr, value);
}

void SlaveInstance::GetString(const cppfmu::FMIValueReference* vr, std::size_t nvr, cppfmu::FMIString* value) const
{
    instance_.getString(vr, nvr, value);
}

SlaveInstance::~SlaveInstance() = default;


} // namespace pythonfmu

std::unique_ptr<pythonfmu::PyState> pyState = nullptr;

cppfmu::UniquePtr<cppfmu::SlaveInstance> CppfmuInstantiateSlave(
    cppfmu::FMIString instanceName,
    cppfmu::FMIString,
    cppfmu::FMIString fmuResourceLocation,
    cppfmu::FMIString,
    cppfmu::FMIReal,
    cppfmu::FMIBoolean,
    cppfmu::FMIBoolean,
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

    return cppfmu::AllocateUnique<pythonfmu::SlaveInstance>(
        memory, instanceName, resources);
}
