
#include <pythonfmu/PythonState.hpp>
#include <pythonfmu/SlaveInstance.hpp>

#include <cppfmu/cppfmu_cs.hpp>

#include <iostream>

namespace pythonfmu
{

SlaveInstance::SlaveInstance(
    const cppfmu::Memory& memory,
    const std::string& resources)
    : instance_(PyObjectWrapper(resources))
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
}

void SlaveInstance::SetInteger(const cppfmu::FMIValueReference* vr, std::size_t nvr, const cppfmu::FMIInteger* value)
{
}

void SlaveInstance::SetBoolean(const cppfmu::FMIValueReference* vr, std::size_t nvr, const cppfmu::FMIBoolean* value)
{
}

void SlaveInstance::SetString(const cppfmu::FMIValueReference* vr, std::size_t nvr, cppfmu::FMIString const* value)
{
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
}

void SlaveInstance::GetString(const cppfmu::FMIValueReference* vr, std::size_t nvr, cppfmu::FMIString* value) const
{
}

SlaveInstance::~SlaveInstance() = default;


} // namespace pythonfmu

pythonfmu::PythonState pythonState;

cppfmu::UniquePtr<cppfmu::SlaveInstance> CppfmuInstantiateSlave(
    cppfmu::FMIString,
    cppfmu::FMIString,
    cppfmu::FMIString fmuResourceLocation,
    cppfmu::FMIString,
    cppfmu::FMIReal,
    cppfmu::FMIBoolean,
    cppfmu::FMIBoolean,
    cppfmu::Memory memory,
    cppfmu::Logger)
{

    auto resources = std::string(fmuResourceLocation);
    auto find = resources.find("file:///");
    if (find != std::string::npos) {
        resources.replace(find, 8, "");
    }

    return cppfmu::AllocateUnique<pythonfmu::SlaveInstance>(
        memory, memory, resources);
}
